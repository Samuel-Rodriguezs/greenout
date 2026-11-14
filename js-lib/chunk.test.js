import { test } from 'node:test';
import assert from 'node:assert/strict';
import { chunk } from './chunk.js';

test('divide em blocos com resto', () => {
  assert.deepEqual(chunk([1, 2, 3, 4, 5], 2), [[1, 2], [3, 4], [5]]);
});
test('lista vazia', () => assert.deepEqual(chunk([], 3), []));
test('tamanho inválido lança erro', () => {
  assert.throws(() => chunk([1], 0), RangeError);
  assert.throws(() => chunk([1], 1.5), RangeError);
});
