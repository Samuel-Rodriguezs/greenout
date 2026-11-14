import test from 'node:test';
import assert from 'node:assert/strict';
import { deCinza, dePixels, obter } from './imagem.js';
import { brilho, contraste, gama, curva, aplicarLUT } from './tons.js';

const g = deCinza(3, 3, [0, 51, 100, 128, 150, 200, 230, 250, 255]);
const vals = (img) => Array.from({ length: img.largura * img.altura }, (_, i) => img.dados[i * 4]);

test('brilho soma e satura', () => {
  assert.deepEqual(vals(brilho(g, 10)), [10, 61, 110, 138, 160, 210, 240, 255, 255]);
  assert.deepEqual(vals(brilho(g, -60)), [0, 0, 40, 68, 90, 140, 170, 190, 195]);
});

test('contraste em torno de 128', () => {
  // (v-128)*2+128
  assert.deepEqual(vals(contraste(g, 2)), [0, 0, 72, 128, 172, 255, 255, 255, 255]);
  assert.deepEqual(vals(contraste(g, 1)), vals(g));
  // fator 0 -> tudo 128
  assert.ok(vals(contraste(g, 0)).every((v) => v === 128));
});

test('gama', () => {
  assert.deepEqual(vals(gama(g, 1)), vals(g));
  const s = gama(g, 2); // 255*sqrt(v/255): 51 -> 114.04
  assert.equal(obter(s, 1, 0)[0], 114);
  assert.equal(obter(s, 0, 0)[0], 0);
  assert.equal(obter(s, 2, 2)[0], 255);
  // gama < 1 escurece: 255*(0.2)^2 = 10.2
  assert.equal(obter(gama(g, 0.5), 1, 0)[0], 10);
  assert.throws(() => gama(g, 0), RangeError);
});

test('curva linear por partes', () => {
  const c = curva(g, [[0, 0], [100, 200], [255, 255]]);
  assert.equal(obter(c, 2, 0)[0], 200); // ponto de controle
  assert.equal(obter(c, 1, 0)[0], 102); // 51 -> 51*2
  // 150: 200 + 50*(55/155) = 217.74
  assert.equal(obter(c, 1, 1)[0], 218);
  assert.throws(() => curva(g, [[0, 0]]));
});

test('aplica a cada canal RGB e preserva alfa', () => {
  const img = dePixels(1, 1, [[10, 20, 30, 99]]);
  assert.deepEqual(obter(brilho(img, 5), 0, 0), [15, 25, 35, 99]);
  const lut = new Uint8Array(256).fill(7);
  assert.deepEqual(obter(aplicarLUT(img, lut), 0, 0), [7, 7, 7, 99]);
});
