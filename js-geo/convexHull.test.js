import test from 'node:test';
import assert from 'node:assert/strict';
import { convexHull } from './convexHull.js';
import { areaComSinal } from './areaCentroide.js';

test('quadrado com pontos internos', () => {
  const h = convexHull([[0, 0], [4, 0], [4, 4], [0, 4], [2, 2], [1, 3], [3, 1]]);
  assert.deepEqual(h, [[0, 0], [4, 0], [4, 4], [0, 4]]);
});

test('resultado é anti-horário', () => {
  const h = convexHull([[0, 0], [5, 1], [3, 6], [-2, 4], [1, 2]]);
  assert.ok(areaComSinal(h) > 0);
  assert.equal(h.length, 4);
});

test('pontos colineares na borda são descartados', () => {
  const h = convexHull([[0, 0], [2, 0], [4, 0], [4, 4], [0, 4]]);
  assert.deepEqual(h, [[0, 0], [4, 0], [4, 4], [0, 4]]);
});

test('duplicatas são ignoradas', () => {
  const h = convexHull([[0, 0], [0, 0], [3, 0], [3, 0], [0, 3]]);
  assert.deepEqual(h, [[0, 0], [3, 0], [0, 3]]);
});

test('casos degenerados: vazio, um, dois pontos', () => {
  assert.deepEqual(convexHull([]), []);
  assert.deepEqual(convexHull([[1, 1]]), [[1, 1]]);
  assert.deepEqual(convexHull([[2, 2], [1, 1]]), [[1, 1], [2, 2]]);
});

test('todos colineares devolvem as duas extremidades', () => {
  assert.deepEqual(convexHull([[0, 0], [1, 1], [2, 2], [3, 3]]), [[0, 0], [3, 3]]);
});

test('não altera a entrada', () => {
  const entrada = [[3, 0], [0, 0], [0, 3]];
  convexHull(entrada);
  assert.deepEqual(entrada, [[3, 0], [0, 0], [0, 3]]);
});
