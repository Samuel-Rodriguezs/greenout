import test from 'node:test';
import assert from 'node:assert/strict';
import { deCinza, dePixels, obter } from './imagem.js';
import { inverter, limiarizar, otsu, limiarOtsu } from './limiar.js';

const vals = (img) => Array.from({ length: img.largura * img.altura }, (_, i) => img.dados[i * 4]);

test('inverter troca RGB e mantém alfa; é involução', () => {
  const img = dePixels(2, 1, [[0, 100, 255, 50], [10, 20, 30, 255]]);
  const inv = inverter(img);
  assert.deepEqual(obter(inv, 0, 0), [255, 155, 0, 50]);
  assert.deepEqual(obter(inv, 1, 0), [245, 235, 225, 255]);
  assert.deepEqual(Array.from(inverter(inv).dados), Array.from(img.dados));
});

test('limiarizar usa comparação estrita', () => {
  const g = deCinza(3, 3, [0, 50, 99, 100, 101, 150, 200, 254, 255]);
  assert.deepEqual(vals(limiarizar(g, 100)), [0, 0, 0, 0, 255, 255, 255, 255, 255]);
  assert.deepEqual(vals(limiarizar(g, 255)), new Array(9).fill(0));
});

test('otsu separa duas classes', () => {
  // 4 pixels escuros (20,30) e 4 claros (200,210): primeiro t com variância máxima = 30
  const g = deCinza(4, 2, [20, 30, 20, 30, 200, 210, 200, 210]);
  assert.equal(otsu(g), 30);
  assert.deepEqual(vals(limiarOtsu(g)), [0, 0, 0, 0, 255, 255, 255, 255]);
});

test('otsu com duas intensidades puras', () => {
  const g = deCinza(2, 2, [0, 200, 0, 200]);
  assert.equal(otsu(g), 0);
});

test('otsu em imagem uniforme devolve 0', () => {
  assert.equal(otsu(deCinza(2, 2, [90, 90, 90, 90])), 0);
});
