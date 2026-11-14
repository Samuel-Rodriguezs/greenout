import test from 'node:test';
import assert from 'node:assert/strict';
import { heapsort } from './heapsort.js';

test('bordas', () => {
  assert.deepEqual(heapsort([]), []);
  assert.deepEqual(heapsort([5]), [5]);
});
test('duplicatas e negativos', () => {
  assert.deepEqual(heapsort([4, -2, 4, 0, -2, 9]), [-2, -2, 0, 4, 4, 9]);
});
test('decrescente com comparador', () => {
  assert.deepEqual(heapsort([1, 3, 2], (a, b) => b - a), [3, 2, 1]);
});
test('aleatório', () => {
  const a = Array.from({ length: 1500 }, () => Math.random() * 1e6 | 0);
  assert.deepEqual(heapsort(a), [...a].sort((x, y) => x - y));
});
