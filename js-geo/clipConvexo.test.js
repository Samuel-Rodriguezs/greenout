import test from 'node:test';
import assert from 'node:assert/strict';
import { recortaPorConvexo, interseccaoConvexos } from './clipConvexo.js';
import { area } from './areaCentroide.js';

const quad = (x, y, l) => [[x, y], [x + l, y], [x + l, y + l], [x, y + l]];

test('quadrados sobrepostos: interseção é o retângulo comum', () => {
  const r = interseccaoConvexos(quad(0, 0, 4), quad(2, 2, 4));
  assert.equal(area(r), 4);
  const xs = r.map((p) => p[0]), ys = r.map((p) => p[1]);
  assert.deepEqual([Math.min(...xs), Math.max(...xs), Math.min(...ys), Math.max(...ys)], [2, 4, 2, 4]);
});

test('polígonos disjuntos dão resultado vazio', () => {
  assert.deepEqual(interseccaoConvexos(quad(0, 0, 1), quad(5, 5, 1)), []);
});

test('um polígono dentro do outro devolve o menor', () => {
  const r = interseccaoConvexos(quad(1, 1, 2), quad(0, 0, 10));
  assert.equal(area(r), 4);
  assert.equal(area(interseccaoConvexos(quad(0, 0, 10), quad(1, 1, 2))), 4);
});

test('janela em sentido horário dá o mesmo resultado', () => {
  const horario = [...quad(2, 2, 4)].reverse();
  assert.equal(area(interseccaoConvexos(quad(0, 0, 4), horario)), 4);
});

test('triângulo recortado por quadrado', () => {
  const tri = [[0, 0], [8, 0], [0, 8]];
  const r = interseccaoConvexos(tri, quad(0, 0, 4));
  // triângulo ∩ [0,4]² = quadrado inteiro (4,4 está sobre a hipotenusa x+y=8)
  assert.ok(Math.abs(area(r) - 16) < 1e-9);
});

test('triângulo com corte diagonal produz pentágono/trapézio com área correta', () => {
  const tri = [[0, 0], [6, 0], [0, 6]];
  const r = interseccaoConvexos(tri, quad(0, 0, 4));
  // quadrado 16 menos o canto acima de x+y=6: triângulo de cateto 2 => 2
  assert.ok(Math.abs(area(r) - 14) < 1e-9);
  assert.equal(r.length, 5);
});

test('operação é comutativa na área para convexos', () => {
  const a = [[0, 0], [5, 1], [4, 5], [-1, 3]];
  const b = [[2, -1], [7, 2], [3, 6]];
  assert.ok(Math.abs(area(interseccaoConvexos(a, b)) - area(interseccaoConvexos(b, a))) < 1e-9);
});

test('sujeito vazio e janela inválida', () => {
  assert.deepEqual(recortaPorConvexo([], quad(0, 0, 1)), []);
  assert.throws(() => recortaPorConvexo(quad(0, 0, 1), [[0, 0], [1, 1]]), RangeError);
});
