import test from 'node:test';
import assert from 'node:assert/strict';
import { fuzzyMatch, fuzzySearch, highlight } from './fuzzy.js';

test('casa subsequência ignorando acento e caixa', () => {
  assert.deepEqual(fuzzyMatch('SAO', 'São Paulo').indices, [0, 1, 2]);
  assert.equal(fuzzyMatch('xyz', 'abc'), null);
  assert.deepEqual(fuzzyMatch('', 'abc'), { score: 0, indices: [] });
});

test('ordem dos caracteres importa', () => {
  assert.equal(fuzzyMatch('ba', 'ab'), null);
});

test('ranking: exato > prefixo > início de palavra > disperso', () => {
  const lista = ['xx a b c', 'abacaxi', 'abc', 'a-b-c longo texto'];
  const r = fuzzySearch('abc', lista).map((x) => x.item);
  assert.deepEqual(r, ['abc', 'a-b-c longo texto', 'xx a b c', 'abacaxi']);
});

test('consecutivos pontuam mais que espalhados', () => {
  const a = fuzzyMatch('rec', 'receita').score;
  const b = fuzzyMatch('rec', 'rua-e-casa').score;
  assert.ok(a > b);
});

test('limit, key e desempate por ordem', () => {
  const itens = [{ n: 'foo' }, { n: 'foo' }, { n: 'food' }];
  const r = fuzzySearch('foo', itens, { key: (x) => x.n, limit: 2 });
  assert.equal(r.length, 2);
  assert.deepEqual(r.map((x) => x.order), [0, 1]);
});

test('highlight agrupa trechos consecutivos', () => {
  const m = fuzzyMatch('rec', 'Receita');
  assert.equal(highlight('Receita', m.indices), '<mark>Rec</mark>eita');
  assert.equal(highlight('abcd', [0, 2], '[', ']'), '[a]b[c]d');
});
