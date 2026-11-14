import test from 'node:test';
import assert from 'node:assert/strict';
import { zFunction, buscaZ } from './zFunction.js';

test('vetor Z', () => {
  assert.deepEqual(zFunction('aabxaab'), [7, 1, 0, 0, 3, 1, 0]);
  assert.deepEqual(zFunction('aaaa'), [4, 3, 2, 1]);
  assert.deepEqual(zFunction('abc'), [3, 0, 0]);
});
test('bordas', () => {
  assert.deepEqual(zFunction(''), []);
  assert.deepEqual(zFunction('a'), [1]);
});
test('busca com Z', () => {
  assert.deepEqual(buscaZ('abracadabra', 'abra'), [0, 7]);
  assert.deepEqual(buscaZ('aaaa', 'aa'), [0, 1, 2]);
});
test('busca sem resultado', () => {
  assert.deepEqual(buscaZ('abc', 'x'), []);
  assert.deepEqual(buscaZ('abc', ''), []);
  assert.deepEqual(buscaZ('', 'a'), []);
});
test('padrão maior que texto', () => assert.deepEqual(buscaZ('ab', 'abc'), []));
