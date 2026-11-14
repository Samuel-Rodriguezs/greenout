import { test } from 'node:test';
import assert from 'node:assert/strict';
import { truncate, truncatePalavras, padEsquerda, padDireita, padCentro } from './truncate.js';

test('truncate', () => {
  assert.equal(truncate('abcdefghij', 6), 'abcde…');
  assert.equal(truncate('curto', 10), 'curto');
  assert.equal(truncate('abcdef', 3, '...'), '...');
});
test('truncatePalavras', () => {
  assert.equal(truncatePalavras('o rato roeu a roupa', 12), 'o rato…');
});
test('pads', () => {
  assert.equal(padEsquerda(7, 3), '007');
  assert.equal(padDireita('ab', 4, '.'), 'ab..');
  assert.equal(padCentro('ab', 5, '*'), '*ab**');
});
