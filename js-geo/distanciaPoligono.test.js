import test from 'node:test';
import assert from 'node:assert/strict';
import {
  distanciaAoContorno, distanciaPontoPoligono, distanciaComSinal, pontoMaisProximoNoContorno,
} from './distanciaPoligono.js';

const quadrado = [[0, 0], [10, 0], [10, 10], [0, 10]];

test('ponto fora: distância à aresta e ao vértice', () => {
  assert.equal(distanciaPontoPoligono([15, 5], quadrado), 5);
  assert.equal(distanciaPontoPoligono([13, 14], quadrado), 5);
});

test('ponto dentro ou na borda tem distância 0 ao polígono', () => {
  assert.equal(distanciaPontoPoligono([5, 5], quadrado), 0);
  assert.equal(distanciaPontoPoligono([10, 3], quadrado), 0);
});

test('distância ao contorno vale também para pontos internos', () => {
  assert.equal(distanciaAoContorno([5, 5], quadrado), 5);
  assert.equal(distanciaAoContorno([2, 5], quadrado), 2);
});

test('distância com sinal', () => {
  assert.equal(distanciaComSinal([2, 5], quadrado), -2);
  assert.equal(distanciaComSinal([-3, 5], quadrado), 3);
  assert.equal(distanciaComSinal([0, 5], quadrado), 0);
});

test('polígono côncavo: ponto no vão do U está fora', () => {
  const u = [[0, 0], [6, 0], [6, 6], [4, 6], [4, 2], [2, 2], [2, 6], [0, 6]];
  assert.equal(distanciaPontoPoligono([3, 5], u), 1);
});

test('ponto mais próximo do contorno', () => {
  assert.deepEqual(pontoMaisProximoNoContorno([15, 5], quadrado), [10, 5]);
  assert.deepEqual(pontoMaisProximoNoContorno([-4, -4], quadrado), [0, 0]);
});

test('polígono inválido lança erro', () => {
  assert.throws(() => distanciaAoContorno([0, 0], [[0, 0], [1, 1]]), RangeError);
});
