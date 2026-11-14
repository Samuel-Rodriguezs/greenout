import test from 'node:test';
import assert from 'node:assert/strict';
import { quicksort } from './quicksort.js';

test('vazio e unitário', () => {
  assert.deepEqual(quicksort([]), []);
  assert.deepEqual(quicksort([7]), [7]);
});
test('ordena com duplicatas e negativos', () => {
  assert.deepEqual(quicksort([3, -1, 3, 0, 2, -1]), [-1, -1, 0, 2, 3, 3]);
});
test('não muda a entrada', () => {
  const a = [3, 2, 1]; quicksort(a); assert.deepEqual(a, [3, 2, 1]);
});
test('já ordenado, reverso e todos iguais', () => {
  const n = 5000;
  const asc = Array.from({ length: n }, (_, i) => i);
  assert.deepEqual(quicksort(asc), asc);
  assert.deepEqual(quicksort([...asc].reverse()), asc);
  assert.deepEqual(quicksort(new Array(n).fill(4)), new Array(n).fill(4));
});
test('comparador customizado', () => {
  assert.deepEqual(quicksort(['bb', 'a', 'ccc'], (x, y) => y.length - x.length), ['ccc', 'bb', 'a']);
});
test('aleatório confere com sort nativo', () => {
  const a = Array.from({ length: 2000 }, () => Math.floor(Math.random() * 100) - 50);
  assert.deepEqual(quicksort(a), [...a].sort((x, y) => x - y));
});
