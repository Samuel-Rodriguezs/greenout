import test from 'node:test';
import assert from 'node:assert/strict';
import { areaComSinal, area, ehAntiHorario, perimetro, centroide, mediaDosPontos } from './areaCentroide.js';

const perto = (a, b, eps = 1e-9) => assert.ok(Math.abs(a - b) <= eps, `${a} != ${b}`);

test('área do retângulo e sinal por orientação', () => {
  const r = [[0, 0], [4, 0], [4, 3], [0, 3]];
  assert.equal(areaComSinal(r), 12);
  assert.equal(areaComSinal([...r].reverse()), -12);
  assert.equal(area([...r].reverse()), 12);
  assert.equal(ehAntiHorario(r), true);
});

test('área do triângulo e polígono côncavo (L)', () => {
  assert.equal(area([[0, 0], [6, 0], [0, 8]]), 24);
  const l = [[0, 0], [4, 0], [4, 1], [1, 1], [1, 4], [0, 4]];
  assert.equal(area(l), 7);
});

test('perímetro do quadrado', () => {
  assert.equal(perimetro([[0, 0], [2, 0], [2, 2], [0, 2]]), 8);
});

test('centroide do retângulo e do triângulo', () => {
  assert.deepEqual(centroide([[0, 0], [4, 0], [4, 2], [0, 2]]), [2, 1]);
  const [x, y] = centroide([[0, 0], [6, 0], [0, 9]]);
  perto(x, 2);
  perto(y, 3);
});

test('centroide do L fica deslocado para o canto cheio', () => {
  const [x, y] = centroide([[0, 0], [4, 0], [4, 1], [1, 1], [1, 4], [0, 4]]);
  perto(x, 9.5 / 7);
  perto(y, 9.5 / 7);
});

test('centroide independe da orientação', () => {
  const p = [[0, 0], [4, 0], [4, 2], [0, 2]];
  assert.deepEqual(centroide([...p].reverse()), [2, 1]);
});

test('degenerado e lista vazia lançam erro', () => {
  assert.throws(() => centroide([[0, 0], [1, 1], [2, 2]]), RangeError);
  assert.throws(() => mediaDosPontos([]), RangeError);
  assert.deepEqual(mediaDosPontos([[0, 0], [2, 4]]), [1, 2]);
});
