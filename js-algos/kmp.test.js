import test from 'node:test';
import assert from 'node:assert/strict';
import { kmp, tabelaPrefixo } from './kmp.js';

test('tabela de prefixo', () => {
  assert.deepEqual(tabelaPrefixo('ABABCABAB'), [0, 0, 1, 2, 0, 1, 2, 3, 4]);
  assert.deepEqual(tabelaPrefixo('aaaa'), [0, 1, 2, 3]);
  assert.deepEqual(tabelaPrefixo(''), []);
});
test('ocorrências simples', () => {
  assert.deepEqual(kmp('ABABDABACDABABCABAB', 'ABABCABAB'), [10]);
});
test('ocorrências sobrepostas', () => {
  assert.deepEqual(kmp('aaaaa', 'aa'), [0, 1, 2, 3]);
  assert.deepEqual(kmp('abababa', 'aba'), [0, 2, 4]);
});
test('sem ocorrência e bordas', () => {
  assert.deepEqual(kmp('abc', 'd'), []);
  assert.deepEqual(kmp('', 'a'), []);
  assert.deepEqual(kmp('abc', ''), []);
  assert.deepEqual(kmp('abc', 'abcd'), []);
  assert.deepEqual(kmp('abc', 'abc'), [0]);
});
test('confere com indexOf em aleatório', () => {
  const txt = Array.from({ length: 300 }, () => 'ab'[Math.random() * 2 | 0]).join('');
  const esperado = [];
  for (let i = txt.indexOf('abba'); i !== -1; i = txt.indexOf('abba', i + 1)) esperado.push(i);
  assert.deepEqual(kmp(txt, 'abba'), esperado);
});
