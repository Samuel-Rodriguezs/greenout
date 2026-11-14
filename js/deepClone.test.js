import { test } from 'node:test';
import assert from 'node:assert/strict';
import { deepClone } from './deepClone.js';

test('primitivos e null voltam iguais', () => {
  assert.equal(deepClone(5), 5);
  assert.equal(deepClone(null), null);
  assert.equal(deepClone(undefined), undefined);
  assert.equal(deepClone('a'), 'a');
});

test('objetos aninhados não compartilham referência', () => {
  const o = { a: { b: [1, { c: 2 }] } };
  const c = deepClone(o);
  assert.deepEqual(c, o);
  assert.notEqual(c.a, o.a);
  assert.notEqual(c.a.b[1], o.a.b[1]);
  c.a.b[1].c = 99;
  assert.equal(o.a.b[1].c, 2);
});

test('clona Date, RegExp, Map e Set', () => {
  const d = new Date(2020, 1, 1);
  const c = deepClone({ d, r: /x+/gi, m: new Map([['k', { v: 1 }]]), s: new Set([1, 2]) });
  assert.notEqual(c.d, d);
  assert.equal(c.d.getTime(), d.getTime());
  assert.equal(c.r.source, 'x+');
  assert.equal(c.r.flags, 'gi');
  assert.deepEqual(c.m.get('k'), { v: 1 });
  assert.ok(c.s.has(2));
});

test('referências circulares são preservadas', () => {
  const o = { nome: 'raiz' };
  o.self = o;
  const c = deepClone(o);
  assert.notEqual(c, o);
  assert.equal(c.self, c);
});

test('mantém protótipo e chaves symbol', () => {
  class P { constructor() { this.x = 1; } }
  const s = Symbol('s');
  const o = new P();
  o[s] = { y: 2 };
  const c = deepClone(o);
  assert.ok(c instanceof P);
  assert.deepEqual(c[s], { y: 2 });
  assert.notEqual(c[s], o[s]);
});

test('arrays esparsos mantêm o tamanho', () => {
  const c = deepClone([1, , 3]);
  assert.equal(c.length, 3);
});
