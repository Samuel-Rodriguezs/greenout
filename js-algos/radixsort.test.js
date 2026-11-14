import test from 'node:test';
import assert from 'node:assert/strict';
import { radixsort } from './radixsort.js';

test('bordas', () => {
  assert.deepEqual(radixsort([]), []);
  assert.deepEqual(radixsort([0]), [0]);
  assert.deepEqual(radixsort([0, 0, 0]), [0, 0, 0]);
});
test('positivos de tamanhos diferentes', () => {
  assert.deepEqual(radixsort([170, 45, 75, 90, 802, 24, 2, 66]), [2, 24, 45, 66, 75, 90, 170, 802]);
});
test('negativos misturados', () => {
  assert.deepEqual(radixsort([3, -10, 0, -2, 25, -300]), [-300, -10, -2, 0, 3, 25]);
});
test('rejeita não inteiros', () => {
  assert.throws(() => radixsort([1, 2.5]), TypeError);
});
test('aleatório', () => {
  const a = Array.from({ length: 1000 }, () => (Math.random() * 20000 | 0) - 10000);
  assert.deepEqual(radixsort(a), [...a].sort((x, y) => x - y));
});
