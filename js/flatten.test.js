import { test } from 'node:test';
import assert from 'node:assert/strict';
import { flatten, flattenTotal } from './flatten.js';

test('profundidade padrão é 1', () => {
  assert.deepEqual(flatten([1, [2, [3]]]), [1, 2, [3]]);
});

test('profundidade 0 mantém a estrutura', () => {
  assert.deepEqual(flatten([1, [2]], 0), [1, [2]]);
});

test('profundidade Infinity achata tudo', () => {
  assert.deepEqual(flatten([1, [2, [3, [4]]]], Infinity), [1, 2, 3, 4]);
});

test('array vazio e subarrays vazios', () => {
  assert.deepEqual(flatten([]), []);
  assert.deepEqual(flatten([[], [[]]], 2), []);
});

test('não achata objetos nem strings', () => {
  assert.deepEqual(flatten([['ab'], [{ a: 1 }]]), ['ab', { a: 1 }]);
});

test('flattenTotal preserva a ordem', () => {
  assert.deepEqual(flattenTotal([1, [2, [3, [4, 5]], 6], [[7]]]), [1, 2, 3, 4, 5, 6, 7]);
});

test('flattenTotal aguenta aninhamento muito profundo', () => {
  let a = [1];
  for (let i = 0; i < 50000; i++) a = [a];
  assert.deepEqual(flattenTotal(a), [1]);
});

test('rejeita não-array', () => {
  assert.throws(() => flatten('abc'), TypeError);
  assert.throws(() => flattenTotal(null), TypeError);
});
