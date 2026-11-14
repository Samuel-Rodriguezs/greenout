import test from 'node:test';
import assert from 'node:assert/strict';
import { countingsort } from './countingsort.js';

test('vazio', () => assert.deepEqual(countingsort([]), []));
test('com negativos', () => {
  assert.deepEqual(countingsort([3, -1, 2, -1, 0]), [-1, -1, 0, 2, 3]);
});
test('estável por chave', () => {
  const r = countingsort([{ k: 2, n: 'a' }, { k: 1, n: 'b' }, { k: 2, n: 'c' }, { k: 1, n: 'd' }], (o) => o.k);
  assert.deepEqual(r.map((o) => o.n), ['b', 'd', 'a', 'c']);
});
test('todos iguais', () => assert.deepEqual(countingsort([5, 5, 5]), [5, 5, 5]));
test('rejeita não inteiro', () => assert.throws(() => countingsort([1.5]), TypeError));
