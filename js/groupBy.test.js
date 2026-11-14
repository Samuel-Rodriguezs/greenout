import { test } from 'node:test';
import assert from 'node:assert/strict';
import { groupBy, contarPor } from './groupBy.js';

test('agrupa por função', () => {
  assert.deepEqual(groupBy([1, 2, 3, 4, 5], (n) => (n % 2 ? 'impar' : 'par')), {
    impar: [1, 3, 5],
    par: [2, 4],
  });
});

test('agrupa por nome de propriedade', () => {
  const pessoas = [
    { nome: 'Ana', cidade: 'SP' },
    { nome: 'Bia', cidade: 'RJ' },
    { nome: 'Caio', cidade: 'SP' },
  ];
  const r = groupBy(pessoas, 'cidade');
  assert.deepEqual(r.SP.map((p) => p.nome), ['Ana', 'Caio']);
  assert.deepEqual(r.RJ.map((p) => p.nome), ['Bia']);
});

test('lista vazia gera objeto vazio', () => {
  assert.deepEqual(groupBy([], 'x'), {});
});

test('chaves como __proto__ ou constructor não quebram', () => {
  const r = groupBy(['a', 'b'], () => 'constructor');
  assert.deepEqual(r.constructor, ['a', 'b']);
});

test('a função recebe o índice', () => {
  const r = groupBy(['a', 'b', 'c', 'd'], (_, i) => i % 2);
  assert.deepEqual(r, { 0: ['a', 'c'], 1: ['b', 'd'] });
});

test('contarPor', () => {
  assert.deepEqual(contarPor(['aa', 'b', 'cc', 'd', 'e'], 'length'), { 1: 3, 2: 2 });
});
