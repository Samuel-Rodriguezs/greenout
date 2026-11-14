import { test } from 'node:test';
import assert from 'node:assert/strict';
import { get, set } from './caminho.js';

test('get com pontos e colchetes', () => {
  const o = { a: { b: [{ c: 5 }] } };
  assert.equal(get(o, 'a.b[0].c'), 5);
  assert.equal(get(o, ['a', 'b', 0, 'c']), 5);
});
test('get com padrão', () => {
  assert.equal(get({ a: null }, 'a.b.c', 'x'), 'x');
  assert.equal(get({ a: 0 }, 'a', 9), 0);
});
test('set cria intermediários', () => {
  const o = set({}, 'a.b[1].c', 7);
  assert.ok(Array.isArray(o.a.b));
  assert.equal(o.a.b.length, 2);
  assert.deepEqual(o.a.b[1], { c: 7 });
});
test('set bloqueia poluição de protótipo', () => {
  set({}, '__proto__.x', 1);
  assert.equal({}.x, undefined);
});
