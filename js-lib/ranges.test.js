import { test } from 'node:test';
import assert from 'node:assert/strict';
import { range, emIntervalo, mesclarIntervalos } from './ranges.js';

test('range', () => {
  assert.deepEqual(range(4), [0, 1, 2, 3]);
  assert.deepEqual(range(1, 10, 3), [1, 4, 7]);
  assert.deepEqual(range(5, 0, -2), [5, 3, 1]);
  assert.throws(() => range(0, 5, 0), RangeError);
});
test('emIntervalo', () => {
  assert.ok(emIntervalo(5, 5, 10));
  assert.ok(!emIntervalo(11, 5, 10));
});
test('mesclarIntervalos', () => {
  assert.deepEqual(mesclarIntervalos([[8, 10], [1, 3], [2, 6], [11, 12]]), [[1, 6], [8, 12]]);
});
