import test from 'node:test';
import assert from 'node:assert/strict';
import { deCinza, dePixels, obter, igual } from './imagem.js';
import { mediana } from './mediana.js';

const vals = (img) => Array.from({ length: img.largura * img.altura }, (_, i) => img.dados[i * 4]);

test('remove ruído sal e pimenta isolado', () => {
  const g = deCinza(5, 5, new Array(25).fill(100).map((v, i) => (i === 12 ? 255 : i === 6 ? 0 : v)));
  const r = mediana(g, 1);
  assert.ok(vals(r).every((v) => v === 100));
});

test('3x3 calculado à mão (borda clamp)', () => {
  const g = deCinza(3, 3, [9, 1, 5, 2, 8, 3, 7, 4, 6]);
  const r = mediana(g, 1);
  // centro: janela inteira {1..9} -> 5
  assert.equal(obter(r, 1, 1)[0], 5);
  // canto (0,0): [9,9,1 / 9,9,1 / 2,2,8] ordenado 1,1,2,2,8,9,9,9,9 -> 8
  assert.equal(obter(r, 0, 0)[0], 8);
});

test('preserva degraus (bordas) melhor que a média', () => {
  const g = deCinza(6, 1, [0, 0, 0, 200, 200, 200]);
  assert.deepEqual(vals(mediana(g, 1)), [0, 0, 0, 200, 200, 200]);
});

test('imagem constante é fixa; modo zero tem janelas parciais', () => {
  const g = deCinza(3, 1, [10, 20, 30]);
  assert.deepEqual(vals(mediana(g, 1, 'zero')), [15, 20, 25]);
  const c = deCinza(3, 3, new Array(9).fill(42));
  assert.ok(igual(mediana(c, 1), c));
});

test('canais tratados separadamente; alfa mantido; validação', () => {
  const img = dePixels(3, 1, [[0, 9, 5, 1], [255, 9, 6, 2], [0, 9, 7, 3]]);
  const r = mediana(img, 1);
  assert.deepEqual(obter(r, 1, 0), [0, 9, 6, 2]);
  assert.throws(() => mediana(img, 0), RangeError);
});
