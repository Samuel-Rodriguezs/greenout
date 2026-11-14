import test from 'node:test';
import assert from 'node:assert/strict';
import { menorTroco, formasDeTroco } from './troco.js';

test('valor zero', () => assert.deepEqual(menorTroco([1, 5], 0), { quantidade: 0, moedas: [] }));
test('caso em que o guloso falha', () => {
  assert.deepEqual(menorTroco([1, 3, 4], 6), { quantidade: 2, moedas: [3, 3] });
});
test('real brasileiro', () => {
  const r = menorTroco([1, 5, 10, 25, 50, 100], 289);
  assert.equal(r.quantidade, 9);
  assert.equal(r.moedas.reduce((a, b) => a + b, 0), 289);
});
test('impossível', () => {
  assert.equal(menorTroco([2], 3), null);
  assert.equal(menorTroco([], 5), null);
});
test('valor inválido', () => {
  assert.throws(() => menorTroco([1], -1), RangeError);
});
test('formas de troco', () => {
  assert.equal(formasDeTroco([1, 2, 5], 5), 4n);
  assert.equal(formasDeTroco([2], 3), 0n);
  assert.equal(formasDeTroco([1, 5, 10, 25, 50, 100], 100), 293n);
  assert.equal(formasDeTroco([3], 0), 1n);
});
