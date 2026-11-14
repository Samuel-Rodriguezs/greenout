import test from 'node:test';
import assert from 'node:assert/strict';
import { orientacao, segmentosSeInterceptam, pontoDeInterseccao } from './segmentos.js';

test('orientação: anti-horário, horário e colinear', () => {
  assert.ok(orientacao([0, 0], [1, 0], [1, 1]) > 0);
  assert.ok(orientacao([0, 0], [1, 0], [1, -1]) < 0);
  assert.equal(orientacao([0, 0], [1, 1], [3, 3]), 0);
});

test('segmentos em X se interceptam', () => {
  assert.equal(segmentosSeInterceptam([0, 0], [4, 4], [0, 4], [4, 0]), true);
});

test('segmentos disjuntos não se interceptam', () => {
  assert.equal(segmentosSeInterceptam([0, 0], [1, 1], [2, 2], [3, 0]), false);
  assert.equal(segmentosSeInterceptam([0, 0], [2, 0], [0, 1], [2, 1]), false);
});

test('toque em extremidade conta como interseção', () => {
  assert.equal(segmentosSeInterceptam([0, 0], [2, 0], [2, 0], [2, 5]), true);
  assert.equal(segmentosSeInterceptam([0, 0], [4, 0], [2, 0], [2, 5]), true);
});

test('colineares: sobrepostos sim, separados não', () => {
  assert.equal(segmentosSeInterceptam([0, 0], [3, 0], [2, 0], [5, 0]), true);
  assert.equal(segmentosSeInterceptam([0, 0], [1, 0], [2, 0], [5, 0]), false);
});

test('ponto de interseção calculado', () => {
  assert.deepEqual(pontoDeInterseccao([0, 0], [4, 4], [0, 4], [4, 0]), [2, 2]);
  assert.deepEqual(pontoDeInterseccao([0, 0], [2, 0], [1, -1], [1, 1]), [1, 0]);
});

test('ponto de interseção: paralelos e fora do segmento retornam null', () => {
  assert.equal(pontoDeInterseccao([0, 0], [1, 0], [0, 1], [1, 1]), null);
  assert.equal(pontoDeInterseccao([0, 0], [1, 1], [3, 0], [0, 3]), null);
  assert.equal(pontoDeInterseccao([0, 0], [1, 0], [5, -1], [5, 1]), null);
  assert.equal(pontoDeInterseccao([0, 0], [3, 0], [1, 0], [2, 0]), null);
});
