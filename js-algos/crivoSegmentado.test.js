import test from 'node:test';
import assert from 'node:assert/strict';
import { crivo, crivoSegmentado, contarPrimos, ehPrimo, fatorar } from './crivoSegmentado.js';

test('crivo simples', () => {
  assert.deepEqual(crivo(30), [2, 3, 5, 7, 11, 13, 17, 19, 23, 29]);
  assert.deepEqual(crivo(1), []);
  assert.deepEqual(crivo(2), [2]);
});
test('segmentado em intervalo', () => {
  assert.deepEqual(crivoSegmentado(10, 50), [11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47]);
});
test('bordas: lo < 2, hi < lo, intervalo unitário', () => {
  assert.deepEqual(crivoSegmentado(-10, 10), [2, 3, 5, 7]);
  assert.deepEqual(crivoSegmentado(10, 5), []);
  assert.deepEqual(crivoSegmentado(-5, 1), []);
  assert.deepEqual(crivoSegmentado(13, 13), [13]);
  assert.deepEqual(crivoSegmentado(14, 14), []);
});
test('segmentos pequenos dão o mesmo resultado', () => {
  assert.deepEqual(crivoSegmentado(2, 1000, 7), crivo(1000));
  assert.deepEqual(crivoSegmentado(2, 1000, 1), crivo(1000));
});
test('contagens conhecidas', () => {
  assert.equal(contarPrimos(100), 25);
  assert.equal(contarPrimos(10000), 1229);
  assert.equal(contarPrimos(1_000_000), 78498);
});
test('intervalo alto', () => {
  const r = crivoSegmentado(1_000_000_000, 1_000_000_100);
  assert.deepEqual(r, [1000000007, 1000000009, 1000000021, 1000000033, 1000000087, 1000000093, 1000000097]);
});
test('limites não inteiros', () => assert.throws(() => crivoSegmentado(1.5, 10), TypeError));
test('ehPrimo', () => {
  assert.deepEqual([0, 1, 2, 3, 4, 5, 25, 97].map(ehPrimo), [false, false, true, true, false, true, false, true]);
  assert.equal(ehPrimo(2147483647), true);
  assert.equal(ehPrimo(-7), false);
  assert.equal(ehPrimo(2.5), false);
});
test('fatorar', () => {
  assert.deepEqual(fatorar(360), { 2: 3, 3: 2, 5: 1 });
  assert.deepEqual(fatorar(97), { 97: 1 });
  assert.deepEqual(fatorar(2), { 2: 1 });
  assert.throws(() => fatorar(1), RangeError);
});
