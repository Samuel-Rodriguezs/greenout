import test from 'node:test';
import assert from 'node:assert/strict';
import { shellsort } from './shellsort.js';

test('bordas', () => {
  assert.deepEqual(shellsort([]), []);
  assert.deepEqual(shellsort([1]), [1]);
  assert.deepEqual(shellsort([2, 1]), [1, 2]);
});
test('strings com comparador', () => {
  assert.deepEqual(shellsort(['b', 'c', 'a'], (x, y) => x.localeCompare(y)), ['a', 'b', 'c']);
});
test('aleatório grande', () => {
  const a = Array.from({ length: 3000 }, () => Math.random() * 1e5 | 0);
  assert.deepEqual(shellsort(a), [...a].sort((x, y) => x - y));
});
test('reverso', () => {
  const a = Array.from({ length: 500 }, (_, i) => 500 - i);
  assert.equal(shellsort(a)[0], 1);
  assert.equal(shellsort(a)[499], 500);
});
