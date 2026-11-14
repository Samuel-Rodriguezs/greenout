import test from 'node:test';
import assert from 'node:assert/strict';
import { dePixels, deCinza, igual, obter } from './imagem.js';
import { codificarPPM, codificarPGM, decodificarPNM } from './pnm.js';

const texto = (b) => String.fromCharCode(...b);

test('PPM: bytes exatos para 2x1', () => {
  const img = dePixels(2, 1, [[255, 0, 0], [1, 2, 3]]);
  const b = codificarPPM(img);
  assert.equal(texto(b.subarray(0, 11)), 'P6\n2 1\n255\n');
  assert.deepEqual(Array.from(b.subarray(11)), [255, 0, 0, 1, 2, 3]);
});

test('PPM ida e volta (alfa vira 255)', () => {
  const img = dePixels(3, 3, Array.from({ length: 9 }, (_, i) => [i * 20, 255 - i * 20, i]));
  assert.ok(igual(decodificarPNM(codificarPPM(img)), img));
});

test('PGM: luma na carga útil e releitura em cinza', () => {
  const img = dePixels(2, 1, [[255, 0, 0], [255, 255, 255]]);
  const b = codificarPGM(img);
  assert.equal(texto(b.subarray(0, 11)), 'P5\n2 1\n255\n');
  assert.deepEqual(Array.from(b.subarray(11)), [76, 255]);
  const r = decodificarPNM(b);
  assert.deepEqual(obter(r, 0, 0), [76, 76, 76, 255]);
});

test('decodifica P3 e P2 ASCII com comentários', () => {
  const p3 = new TextEncoder().encode('P3\n# comentario\n2 1\n255\n255 0 0  0 0 255\n');
  const r = decodificarPNM(p3);
  assert.deepEqual(obter(r, 0, 0), [255, 0, 0, 255]);
  assert.deepEqual(obter(r, 1, 0), [0, 0, 255, 255]);
  const p2 = new TextEncoder().encode('P2 2 2 255 0 64 128 255');
  assert.deepEqual(Array.from(decodificarPNM(p2).dados).filter((_, i) => i % 4 === 0), [0, 64, 128, 255]);
});

test('maxval menor é reescalado', () => {
  const r = decodificarPNM(new TextEncoder().encode('P2\n2 1\n15\n0 15\n'));
  assert.deepEqual([obter(r, 0, 0)[0], obter(r, 1, 0)[0]], [0, 255]);
});

test('erros: formato, truncamento', () => {
  assert.throws(() => decodificarPNM(new TextEncoder().encode('P9 1 1 255 0')), /não suportado/);
  assert.throws(() => decodificarPNM(Uint8Array.from([...new TextEncoder().encode('P6\n2 2\n255\n'), 1, 2, 3])), /truncado/);
  assert.throws(() => decodificarPNM(new TextEncoder().encode('P2 2 2 255 1 2')), /truncado/);
  const g = deCinza(1, 1, [9]);
  assert.equal(codificarPGM(g).length, 11 + 1);
});
