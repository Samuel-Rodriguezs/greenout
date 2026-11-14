import test from 'node:test';
import assert from 'node:assert/strict';
import { lcs, tamanhoLcs } from './lcs.js';

test('strings clássicas', () => {
  assert.equal(tamanhoLcs('AGGTAB', 'GXTXAYB'), 4);
  assert.equal(lcs('AGGTAB', 'GXTXAYB'), 'GTAB');
});
test('vazios', () => {
  assert.equal(lcs('', 'abc'), '');
  assert.equal(lcs('abc', ''), '');
  assert.equal(lcs('', ''), '');
});
test('sem nada em comum', () => assert.equal(lcs('abc', 'xyz'), ''));
test('iguais', () => assert.equal(lcs('banana', 'banana'), 'banana'));
test('resultado é subsequência de ambas', () => {
  const ehSub = (s, t) => { let i = 0; for (const c of t) if (c === s[i]) i++; return i === s.length; };
  const r = lcs('abcbdab', 'bdcaba');
  assert.equal(r.length, 4);
  assert.equal(ehSub(r, 'abcbdab') && ehSub(r, 'bdcaba'), true);
});
test('funciona com arrays', () => {
  assert.deepEqual(lcs([1, 2, 3, 4], [2, 4, 5]), [2, 4]);
});
