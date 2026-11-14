import test from 'node:test';
import assert from 'node:assert/strict';
import { mergesort } from './mergesort.js';

test('bordas', () => {
  assert.deepEqual(mergesort([]), []);
  assert.deepEqual(mergesort([1]), [1]);
  assert.deepEqual(mergesort([2, 1]), [1, 2]);
});
test('é estável', () => {
  const itens = [{ k: 1, n: 'a' }, { k: 0, n: 'b' }, { k: 1, n: 'c' }, { k: 0, n: 'd' }];
  const r = mergesort(itens, (x, y) => x.k - y.k).map((o) => o.n);
  assert.deepEqual(r, ['b', 'd', 'a', 'c']);
});
test('não muda a entrada', () => {
  const a = [3, 1, 2]; mergesort(a); assert.deepEqual(a, [3, 1, 2]);
});
test('aleatório', () => {
  const a = Array.from({ length: 1500 }, () => Math.random() * 1000 | 0);
  assert.deepEqual(mergesort(a), [...a].sort((x, y) => x - y));
});
