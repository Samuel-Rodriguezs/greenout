import test from 'node:test';
import assert from 'node:assert/strict';
import { lis, tamanhoLis } from './lis.js';

test('vazio e unitário', () => {
  assert.deepEqual(lis([]), []);
  assert.deepEqual(lis([4]), [4]);
});
test('exemplo clássico', () => {
  assert.equal(tamanhoLis([10, 9, 2, 5, 3, 7, 101, 18]), 4);
});
test('já crescente e decrescente', () => {
  assert.deepEqual(lis([1, 2, 3, 4]), [1, 2, 3, 4]);
  assert.equal(tamanhoLis([4, 3, 2, 1]), 1);
});
test('estrita: iguais não contam', () => {
  assert.equal(tamanhoLis([2, 2, 2]), 1);
  assert.equal(tamanhoLis([1, 2, 2, 3]), 3);
});
test('reconstrução é crescente e subsequência', () => {
  const v = [0, 8, 4, 12, 2, 10, 6, 14, 1, 9, 5, 13, 3, 11, 7, 15];
  const r = lis(v);
  assert.equal(r.length, 6);
  for (let i = 1; i < r.length; i++) assert.ok(r[i] > r[i - 1]);
  let k = 0;
  for (const x of v) if (x === r[k]) k++;
  assert.equal(k, r.length);
});
test('negativos', () => assert.deepEqual(lis([-3, -1, -2, 0]), [-3, -2, 0]));
