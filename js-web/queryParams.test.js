import test from 'node:test';
import assert from 'node:assert/strict';
import { parseQuery, buildQuery } from './queryParams.js';

test('strings por padrão', () => {
  assert.deepEqual(parseQuery('https://x.com/p?a=1&b=dois#h'), { a: '1', b: 'dois' });
});

test('tipos number e boolean', () => {
  const r = parseQuery('?pagina=3&ativo=true&off=0&ruim=abc', { pagina: 'number', ativo: 'boolean', off: 'boolean', ruim: 'number' });
  assert.deepEqual(r, { pagina: 3, ativo: true, off: false });
});

test('arrays por repetição e por colchetes', () => {
  assert.deepEqual(parseQuery('?t=a&t=b&c[]=1', { c: 'number' }), { t: ['a', 'b'], c: [1] });
  assert.deepEqual(parseQuery('?x=1', { x: { tipo: 'number', array: true } }), { x: [1] });
});

test('date e json', () => {
  const r = parseQuery('?d=2024-05-01&f=%7B%22a%22%3A1%7D', { d: 'date', f: 'json' });
  assert.equal(r.d.toISOString(), '2024-05-01T00:00:00.000Z');
  assert.deepEqual(r.f, { a: 1 });
});

test('valores padrão', () => {
  assert.deepEqual(parseQuery('?', { ordem: { tipo: 'string', padrao: 'asc' } }), { ordem: 'asc' });
});

test('tipo desconhecido lança', () => {
  assert.throws(() => parseQuery('?a=1', { a: 'xyz' }));
});

test('buildQuery faz round-trip', () => {
  const q = buildQuery({ a: 1, ok: true, tags: ['x', 'y z'], nada: null });
  assert.equal(q, '?a=1&ok=true&tags%5B%5D=x&tags%5B%5D=y+z');
  assert.deepEqual(parseQuery(q, { a: 'number', ok: 'boolean' }), { a: 1, ok: true, tags: ['x', 'y z'] });
  assert.equal(buildQuery({}), '');
});
