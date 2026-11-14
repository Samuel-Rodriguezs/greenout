import { test } from 'node:test';
import assert from 'node:assert/strict';
import { zip, unzip } from './zip.js';

test('zip combina posições', () => {
  assert.deepEqual(zip([1, 2], ['a', 'b']), [[1, 'a'], [2, 'b']]);
});
test('zip corta no menor', () => assert.deepEqual(zip([1, 2, 3], ['a']), [[1, 'a']]));
test('zip sem argumentos', () => assert.deepEqual(zip(), []));
test('unzip inverte zip', () => {
  const a = [1, 2, 3], b = ['x', 'y', 'z'];
  assert.deepEqual(unzip(zip(a, b)), [a, b]);
});
