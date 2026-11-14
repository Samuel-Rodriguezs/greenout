import { test } from 'node:test';
import assert from 'node:assert/strict';
import { sortBy } from './sort-by.js';

const gente = [
  { n: 'Ana', i: 30 }, { n: 'Bia', i: 25 }, { n: 'Caio', i: 30 },
];
test('por propriedade', () => assert.deepEqual(sortBy(gente, 'i').map((p) => p.n), ['Bia', 'Ana', 'Caio']));
test('decrescente e desempate', () => {
  assert.deepEqual(sortBy(gente, '-i', '-n').map((p) => p.n), ['Caio', 'Ana', 'Bia']);
});
test('não muta o original', () => {
  const c = [3, 1, 2];
  sortBy(c, (x) => x);
  assert.deepEqual(c, [3, 1, 2]);
});
