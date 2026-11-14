import { test } from 'node:test';
import assert from 'node:assert/strict';
import { pick, omit } from './pick-omit.js';

const o = { a: 1, b: 2, c: 3 };
test('pick', () => assert.deepEqual(pick(o, ['a', 'c', 'z']), { a: 1, c: 3 }));
test('omit', () => assert.deepEqual(omit(o, ['b']), { a: 1, c: 3 }));
test('não mutam', () => {
  pick(o, ['a']); omit(o, ['a']);
  assert.deepEqual(o, { a: 1, b: 2, c: 3 });
});
