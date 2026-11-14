import test from 'node:test';
import assert from 'node:assert/strict';
import {
  criaBBox, bboxDePontos, largura, altura, areaBBox, centroBBox, contemPonto, contemBBox,
  intersecta, interseccao, uniao, expande, distanciaAoPonto,
} from './bbox.js';

test('bbox de pontos e métricas', () => {
  const b = bboxDePontos([[1, 5], [-2, 3], [4, -1]]);
  assert.deepEqual({ ...b }, { minX: -2, minY: -1, maxX: 4, maxY: 5 });
  assert.equal(largura(b), 6);
  assert.equal(altura(b), 6);
  assert.equal(areaBBox(b), 36);
  assert.deepEqual(centroBBox(b), [1, 2]);
});

test('caixa é imutável e valida inversão', () => {
  const b = criaBBox(0, 0, 1, 1);
  assert.ok(Object.isFrozen(b));
  assert.throws(() => criaBBox(2, 0, 1, 1), RangeError);
  assert.throws(() => bboxDePontos([]), RangeError);
});

test('contenção de ponto inclui a borda', () => {
  const b = criaBBox(0, 0, 10, 10);
  assert.equal(contemPonto(b, [10, 10]), true);
  assert.equal(contemPonto(b, [10.1, 5]), false);
});

test('interseção, toque e disjunção', () => {
  const a = criaBBox(0, 0, 4, 4);
  assert.equal(intersecta(a, criaBBox(4, 4, 6, 6)), true);
  assert.equal(intersecta(a, criaBBox(5, 0, 6, 1)), false);
  assert.deepEqual({ ...interseccao(a, criaBBox(2, 1, 8, 3)) }, { minX: 2, minY: 1, maxX: 4, maxY: 3 });
  assert.equal(interseccao(a, criaBBox(5, 5, 6, 6)), null);
});

test('união, contenção de caixa e expansão', () => {
  const a = criaBBox(0, 0, 1, 1), b = criaBBox(3, -2, 4, 0);
  const u = uniao(a, b);
  assert.deepEqual({ ...u }, { minX: 0, minY: -2, maxX: 4, maxY: 1 });
  assert.equal(contemBBox(u, a), true);
  assert.equal(contemBBox(a, u), false);
  assert.deepEqual({ ...expande(a, 2) }, { minX: -2, minY: -2, maxX: 3, maxY: 3 });
});

test('distância ponto-caixa', () => {
  const b = criaBBox(0, 0, 2, 2);
  assert.equal(distanciaAoPonto(b, [1, 1]), 0);
  assert.equal(distanciaAoPonto(b, [5, 1]), 3);
  assert.equal(distanciaAoPonto(b, [5, 6]), 5);
});
