import { test } from 'node:test';
import assert from 'node:assert/strict';
import { mergeDeep } from './merge-deep.js';

test('mescla aninhado', () => {
  assert.deepEqual(mergeDeep({ a: { x: 1, y: 2 }, b: 1 }, { a: { y: 3 }, c: 4 }), { a: { x: 1, y: 3 }, b: 1, c: 4 });
});
test('arrays são substituídos', () => assert.deepEqual(mergeDeep({ l: [1, 2] }, { l: [3] }), { l: [3] }));
test('não muta entradas', () => {
  const a = { o: { x: 1 } }, b = { o: { y: 2 } };
  const r = mergeDeep(a, b);
  r.o.x = 99;
  assert.equal(a.o.x, 1);
});
test('ignora __proto__', () => {
  const r = mergeDeep({}, JSON.parse('{"__proto__":{"hack":true}}'));
  assert.equal({}.hack, undefined);
  assert.equal(r.hack, undefined);
});
