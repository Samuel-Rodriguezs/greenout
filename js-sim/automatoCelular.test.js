import test from 'node:test';
import assert from 'node:assert/strict';
import { regra, proximaGeracao, simular, sementeCentral, renderizar } from './automatoCelular.js';

test('tabela da regra 30', () => {
  const f = regra(30);
  const saidas = [[1, 1, 1], [1, 1, 0], [1, 0, 1], [1, 0, 0], [0, 1, 1], [0, 1, 0], [0, 0, 1], [0, 0, 0]].map((t) => f(...t));
  assert.deepEqual(saidas, [0, 0, 0, 1, 1, 1, 1, 0]);
});

test('regra fora do intervalo lança erro', () => {
  assert.throws(() => regra(256));
  assert.throws(() => regra(-1));
  assert.throws(() => regra(1.5));
});

test('regra 30 a partir de uma célula', () => {
  const h = simular(sementeCentral(7), 30, 3);
  assert.deepEqual(h[1], [0, 0, 1, 1, 1, 0, 0]);
  assert.deepEqual(h[2], [0, 1, 1, 0, 0, 1, 0]);
});

test('regra 90 gera triângulo de Sierpinski', () => {
  const h = simular(sementeCentral(15), 90, 4);
  assert.equal(renderizar(h), [
    '.......#.......',
    '......#.#......',
    '.....#...#.....',
    '....#.#.#.#....',
  ].join('\n'));
});

test('regra 255 acende tudo e regra 0 apaga tudo', () => {
  assert.deepEqual(proximaGeracao([0, 1, 0, 0], 255), [1, 1, 1, 1]);
  assert.deepEqual(proximaGeracao([1, 1, 1, 1], 0), [0, 0, 0, 0]);
});

test('regra 204 (identidade) e 170 (desloca) ', () => {
  const x = [1, 0, 1, 1, 0];
  assert.deepEqual(proximaGeracao(x, 204), x);
  assert.deepEqual(proximaGeracao(x, 170), [0, 1, 1, 0, 1]); // copia o vizinho da direita
});

test('bordas circulares vs fixas', () => {
  const x = [1, 0, 0, 0, 0];
  assert.deepEqual(proximaGeracao(x, 2, true), [0, 0, 0, 0, 1]);
  assert.deepEqual(proximaGeracao(x, 2, false), [0, 0, 0, 0, 0]);
});

test('simular com 1 geração devolve só a inicial', () => {
  const s = sementeCentral(5);
  assert.deepEqual(simular(s, 30, 1), [s]);
});
