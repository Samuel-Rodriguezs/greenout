import test from 'node:test';
import assert from 'node:assert/strict';
import { classificaPonto, pontoEmPoligono } from './pontoEmPoligono.js';

const quadrado = [[0, 0], [4, 0], [4, 4], [0, 4]];
// Polígono em "U" (côncavo)
const u = [[0, 0], [6, 0], [6, 6], [4, 6], [4, 2], [2, 2], [2, 6], [0, 6]];

test('ponto dentro, fora e na borda do quadrado', () => {
  assert.equal(classificaPonto([2, 2], quadrado), 'dentro');
  assert.equal(classificaPonto([5, 2], quadrado), 'fora');
  assert.equal(classificaPonto([4, 2], quadrado), 'borda');
  assert.equal(classificaPonto([0, 0], quadrado), 'borda');
});

test('polígono côncavo: vão do U está fora', () => {
  assert.equal(classificaPonto([3, 4], u), 'fora');
  assert.equal(classificaPonto([1, 4], u), 'dentro');
  assert.equal(classificaPonto([3, 1], u), 'dentro');
});

test('independe da orientação do anel', () => {
  const horario = [...quadrado].reverse();
  assert.equal(classificaPonto([1, 1], horario), 'dentro');
});

test('raio passando exatamente por vértice não gera erro', () => {
  const losango = [[0, 2], [2, 0], [4, 2], [2, 4]];
  assert.equal(classificaPonto([-1, 2], losango), 'fora');
  assert.equal(classificaPonto([2, 2], losango), 'dentro');
});

test('anel fechado explicitamente é aceito', () => {
  assert.equal(classificaPonto([1, 1], [...quadrado, [0, 0]]), 'dentro');
});

test('incluiBorda controla o resultado booleano', () => {
  assert.equal(pontoEmPoligono([4, 2], quadrado), true);
  assert.equal(pontoEmPoligono([4, 2], quadrado, { incluiBorda: false }), false);
  assert.equal(pontoEmPoligono([2, 2], quadrado, { incluiBorda: false }), true);
});

test('menos de 3 vértices lança erro', () => {
  assert.throws(() => classificaPonto([0, 0], [[0, 0], [1, 1]]), RangeError);
});
