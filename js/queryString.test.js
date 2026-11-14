import { test } from 'node:test';
import assert from 'node:assert/strict';
import { parseQuery, stringifyQuery } from './queryString.js';

test('parse básico, com e sem "?"', () => {
  assert.deepEqual(parseQuery('a=1&b=2'), { a: '1', b: '2' });
  assert.deepEqual(parseQuery('?a=1&b=2'), { a: '1', b: '2' });
  assert.deepEqual(parseQuery('http://x.com/p?a=1#topo'), { a: '1' });
});

test('entrada vazia', () => {
  assert.deepEqual(parseQuery(''), {});
  assert.deepEqual(parseQuery('?'), {});
  assert.deepEqual(parseQuery(undefined), {});
});

test('chaves repetidas viram array', () => {
  assert.deepEqual(parseQuery('t=a&t=b&t=c'), { t: ['a', 'b', 'c'] });
});

test('decodifica %XX e +', () => {
  assert.deepEqual(parseQuery('nome=Jos%C3%A9+Silva'), { nome: 'José Silva' });
});

test('chave sem valor e valor vazio', () => {
  assert.deepEqual(parseQuery('flag&v='), { flag: '', v: '' });
});

test('valor contendo "="', () => {
  assert.deepEqual(parseQuery('q=a=b'), { q: 'a=b' });
});

test('percent malformado não lança', () => {
  assert.deepEqual(parseQuery('a=%E0%A4%A'), { a: '%E0%A4%A' });
});

test('chave __proto__ não polui o protótipo', () => {
  const r = parseQuery('__proto__=x');
  assert.equal(Object.getPrototypeOf(r), Object.prototype);
  assert.equal({}.x, undefined);
});

test('stringify codifica e expande arrays', () => {
  assert.equal(stringifyQuery({ q: 'a b', t: ['x', 'y'] }), 'q=a%20b&t=x&t=y');
});

test('stringify ignora null/undefined e mantém 0', () => {
  assert.equal(stringifyQuery({ a: null, b: undefined, c: 0 }), 'c=0');
});

test('ida e volta', () => {
  const o = { nome: 'João & Maria', ids: ['1', '2'] };
  assert.deepEqual(parseQuery(stringifyQuery(o)), o);
});
