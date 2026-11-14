import test from 'node:test';
import assert from 'node:assert/strict';
import { buscaBinaria, limiteInferior, limiteSuperior, contar, buscaNaResposta } from './buscaBinaria.js';

const v = [1, 2, 2, 2, 5, 7, 7, 10];

test('vetor vazio', () => {
  assert.equal(buscaBinaria([], 1), -1);
  assert.equal(limiteInferior([], 1), 0);
  assert.equal(limiteSuperior([], 1), 0);
});
test('limites com duplicatas', () => {
  assert.equal(limiteInferior(v, 2), 1);
  assert.equal(limiteSuperior(v, 2), 4);
  assert.equal(contar(v, 2), 3);
  assert.equal(contar(v, 7), 2);
  assert.equal(contar(v, 3), 0);
});
test('fora dos extremos', () => {
  assert.equal(limiteInferior(v, 0), 0);
  assert.equal(limiteInferior(v, 11), v.length);
  assert.equal(limiteSuperior(v, 10), v.length);
});
test('buscaBinaria acha ou devolve -1', () => {
  assert.equal(buscaBinaria(v, 5), 4);
  assert.equal(buscaBinaria(v, 10), 7);
  assert.equal(buscaBinaria(v, 6), -1);
  assert.equal(v[buscaBinaria(v, 2)], 2);
});
test('comparador customizado', () => {
  const palavras = ['a', 'bb', 'ccc', 'dddd'];
  assert.equal(buscaBinaria(palavras, 'xxx', (p, q) => p.length - q.length), 2);
});
test('busca na resposta: raiz quadrada inteira', () => {
  const raiz = (n) => buscaNaResposta(0, n, (k) => k * k > n) - 1;
  assert.equal(raiz(0), 0);
  assert.equal(raiz(26), 5);
  assert.equal(raiz(1000000), 1000);
  assert.equal(buscaNaResposta(0, 10, () => false), 11);
});
