import { test } from 'node:test';
import assert from 'node:assert/strict';
import { parseSemver, compararSemver, ordenarVersoes } from './semver.js';

test('parse', () => {
  assert.deepEqual(parseSemver('v1.2.3-beta.1+build'), { major: 1, minor: 2, patch: 3, pre: ['beta', '1'] });
  assert.throws(() => parseSemver('1.2'), TypeError);
});
test('comparação numérica, não lexicográfica', () => {
  assert.equal(compararSemver('1.10.0', '1.9.0'), 1);
  assert.equal(compararSemver('1.0.0', '1.0.0+x'), 0);
  assert.equal(compararSemver('0.9.9', '1.0.0'), -1);
});
test('pre-release', () => {
  assert.equal(compararSemver('1.0.0-alpha', '1.0.0'), -1);
  assert.equal(compararSemver('1.0.0-alpha.1', '1.0.0-alpha.beta'), -1);
  assert.equal(compararSemver('1.0.0-beta.2', '1.0.0-beta.11'), -1);
  assert.equal(compararSemver('1.0.0-alpha', '1.0.0-alpha.1'), -1);
});
test('ordenar segue a spec', () => {
  const r = ordenarVersoes(['1.0.0', '1.0.0-rc.1', '1.0.0-alpha', '0.1.0', '1.0.0-beta']);
  assert.deepEqual(r, ['0.1.0', '1.0.0-alpha', '1.0.0-beta', '1.0.0-rc.1', '1.0.0']);
});
