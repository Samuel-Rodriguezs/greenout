import test from 'node:test';
import assert from 'node:assert/strict';
import { rabinKarp, rabinKarpMultiplo } from './rabinKarp.js';

test('ocorrências básicas', () => {
  assert.deepEqual(rabinKarp('GEEKS FOR GEEKS', 'GEEK'), [0, 10]);
});
test('sobrepostas', () => assert.deepEqual(rabinKarp('aaaa', 'aa'), [0, 1, 2]));
test('bordas', () => {
  assert.deepEqual(rabinKarp('abc', ''), []);
  assert.deepEqual(rabinKarp('', 'a'), []);
  assert.deepEqual(rabinKarp('ab', 'abc'), []);
  assert.deepEqual(rabinKarp('abc', 'abc'), [0]);
  assert.deepEqual(rabinKarp('a', 'a'), [0]);
});
test('ocorrência no final', () => assert.deepEqual(rabinKarp('xxxab', 'ab'), [3]));
test('unicode', () => assert.deepEqual(rabinKarp('ação e ação', 'ação'), [0, 7]));
test('múltiplos padrões', () => {
  assert.deepEqual(rabinKarpMultiplo('abcabc', ['ab', 'ca', 'zz']), { ab: [0, 3], ca: [2], zz: [] });
});
test('texto longo confere com indexOf', () => {
  const t = 'abcde'.repeat(2000) + 'XYZ';
  assert.deepEqual(rabinKarp(t, 'eaXY'), []);
  assert.deepEqual(rabinKarp(t, 'eXYZ'), [t.length - 4]);
});
