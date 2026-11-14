import { test } from 'node:test';
import assert from 'node:assert/strict';
import { transpor, ehSimetrica, rotacionarHorario } from './transposta.js';

test('transpõe matriz retangular', () => {
  assert.deepEqual(transpor([[1, 2, 3], [4, 5, 6]]), [[1, 4], [2, 5], [3, 6]]);
});

test('transpõe matriz quadrada e 1x1', () => {
  assert.deepEqual(transpor([[1, 2], [3, 4]]), [[1, 3], [2, 4]]);
  assert.deepEqual(transpor([[9]]), [[9]]);
});

test('vetor linha vira vetor coluna', () => {
  assert.deepEqual(transpor([[1, 2, 3]]), [[1], [2], [3]]);
});

test('matriz vazia', () => {
  assert.deepEqual(transpor([]), []);
});

test('transposta da transposta é a original e não muta a entrada', () => {
  const m = [[1, 2], [3, 4], [5, 6]];
  const copia = JSON.parse(JSON.stringify(m));
  assert.deepEqual(transpor(transpor(m)), m);
  assert.deepEqual(m, copia);
});

test('rejeita matriz irregular ou inválida', () => {
  assert.throws(() => transpor([[1, 2], [3]]), RangeError);
  assert.throws(() => transpor([1, 2]), TypeError);
  assert.throws(() => transpor('abc'), TypeError);
});

test('ehSimetrica', () => {
  assert.ok(ehSimetrica([[1, 2], [2, 1]]));
  assert.ok(!ehSimetrica([[1, 2], [3, 1]]));
  assert.ok(!ehSimetrica([[1, 2, 3], [4, 5, 6]]));
  assert.ok(ehSimetrica([]));
});

test('rotacionarHorario', () => {
  assert.deepEqual(rotacionarHorario([[1, 2], [3, 4]]), [[3, 1], [4, 2]]);
  assert.deepEqual(rotacionarHorario([[1, 2, 3]]), [[1], [2], [3]]);
});
