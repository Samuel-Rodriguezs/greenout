import { test } from 'node:test';
import assert from 'node:assert/strict';
import { partition } from './partition.js';

test('pares e ímpares', () => {
  assert.deepEqual(partition([1, 2, 3, 4, 5], (n) => n % 2 === 0), [[2, 4], [1, 3, 5]]);
});
test('vazio', () => assert.deepEqual(partition([], () => true), [[], []]));
test('recebe o índice', () => assert.deepEqual(partition(['a', 'b', 'c'], (_, i) => i === 1), [['b'], ['a', 'c']]));
