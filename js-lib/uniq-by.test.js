import { test } from 'node:test';
import assert from 'node:assert/strict';
import { uniqBy } from './uniq-by.js';

test('identidade por padrão', () => assert.deepEqual(uniqBy([1, 2, 1, 3, 2]), [1, 2, 3]));
test('por função', () => {
  assert.deepEqual(uniqBy([1.1, 1.9, 2.3], Math.floor), [1.1, 2.3]);
});
test('por nome de propriedade', () => {
  const r = uniqBy([{ id: 1, n: 'a' }, { id: 1, n: 'b' }, { id: 2, n: 'c' }], 'id');
  assert.deepEqual(r.map((o) => o.n), ['a', 'c']);
});
