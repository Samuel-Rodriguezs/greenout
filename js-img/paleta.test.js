import test from 'node:test';
import assert from 'node:assert/strict';
import { dePixels, obter, igual } from './imagem.js';
import { medianCut, maisProxima, aplicarPaleta, quantizar } from './paleta.js';

const quatro = dePixels(2, 2, [[255, 0, 0], [0, 255, 0], [0, 0, 255], [255, 255, 255]]);

test('4 cores distintas com n=4 devolvem as mesmas cores', () => {
  const p = medianCut(quatro, 4);
  const chave = (c) => c.join(',');
  assert.deepEqual(p.map(chave).sort(), ['0,0,255', '0,255,0', '255,0,0', '255,255,255']);
  assert.ok(igual(quantizar(quatro, 4), quatro));
});

test('n=2 agrupa tons escuros e claros pela média', () => {
  const img = dePixels(2, 2, [[10, 10, 10], [20, 20, 20], [200, 200, 200], [210, 210, 210]]);
  assert.deepEqual(medianCut(img, 2), [[15, 15, 15], [205, 205, 205]]);
});

test('n=1 devolve a média de tudo', () => {
  const img = dePixels(2, 1, [[0, 100, 200], [100, 200, 0]]);
  assert.deepEqual(medianCut(img, 1), [[50, 150, 100]]);
});

test('não gera mais cores do que existem', () => {
  const img = dePixels(2, 2, [[5, 5, 5], [5, 5, 5], [9, 9, 9], [9, 9, 9]]);
  assert.deepEqual(medianCut(img, 8), [[5, 5, 5], [9, 9, 9]]);
});

test('divide pelo canal de maior faixa', () => {
  // só o canal B varia muito: separa por B
  const img = dePixels(4, 1, [[100, 100, 0], [100, 100, 10], [100, 102, 250], [100, 100, 254]]);
  assert.deepEqual(medianCut(img, 2), [[100, 100, 5], [100, 101, 252]]);
});

test('maisProxima e aplicarPaleta preservam alfa', () => {
  const paleta = [[0, 0, 0], [255, 255, 255]];
  assert.equal(maisProxima(paleta, 100, 100, 100), 0);
  assert.equal(maisProxima(paleta, 200, 180, 190), 1);
  const img = dePixels(2, 1, [[90, 90, 90, 40], [250, 250, 250, 255]]);
  const r = aplicarPaleta(img, paleta);
  assert.deepEqual(obter(r, 0, 0), [0, 0, 0, 40]);
  assert.deepEqual(obter(r, 1, 0), [255, 255, 255, 255]);
  assert.throws(() => medianCut(img, 0), RangeError);
});
