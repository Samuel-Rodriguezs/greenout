import test from 'node:test';
import assert from 'node:assert/strict';
import { triangula } from './earClipping.js';
import { area, areaComSinal } from './areaCentroide.js';

const somaAreas = (poly, tris) => tris.reduce((s, t) => s + area(t.map((i) => poly[i])), 0);

test('triângulo devolve ele mesmo', () => {
  const t = triangula([[0, 0], [4, 0], [0, 3]]);
  assert.equal(t.length, 1);
  assert.deepEqual([...t[0]].sort(), [0, 1, 2]);
});

test('quadrado vira 2 triângulos cuja área soma 16', () => {
  const q = [[0, 0], [4, 0], [4, 4], [0, 4]];
  const t = triangula(q);
  assert.equal(t.length, 2);
  assert.equal(somaAreas(q, t), 16);
});

test('polígono côncavo em L: n-2 triângulos e área preservada', () => {
  const l = [[0, 0], [4, 0], [4, 1], [1, 1], [1, 4], [0, 4]];
  const t = triangula(l);
  assert.equal(t.length, 4);
  assert.equal(somaAreas(l, t), 7);
});

test('polígono em U e em estrela preservam a área', () => {
  const u = [[0, 0], [6, 0], [6, 6], [4, 6], [4, 2], [2, 2], [2, 6], [0, 6]];
  assert.equal(somaAreas(u, triangula(u)), area(u));
  const estrela = [];
  for (let k = 0; k < 10; k++) {
    const r = k % 2 === 0 ? 10 : 4;
    const a = (Math.PI * 2 * k) / 10;
    estrela.push([r * Math.cos(a), r * Math.sin(a)]);
  }
  const t = triangula(estrela);
  assert.equal(t.length, 8);
  assert.ok(Math.abs(somaAreas(estrela, t) - area(estrela)) < 1e-9);
});

test('entrada em sentido horário também funciona e saída é anti-horária', () => {
  const horario = [[0, 0], [0, 4], [4, 4], [4, 0]];
  const t = triangula(horario);
  assert.equal(t.length, 2);
  for (const tri of t) assert.ok(areaComSinal(tri.map((i) => horario[i])) > 0);
});

test('vértice colinear em aresta não quebra a triangulação', () => {
  const q = [[0, 0], [2, 0], [4, 0], [4, 4], [0, 4]];
  const t = triangula(q);
  assert.equal(somaAreas(q, t), 16);
});

test('cada índice é usado e todos os triângulos têm área positiva', () => {
  const p = [[0, 0], [5, 0], [6, 3], [3, 6], [-1, 4]];
  const t = triangula(p);
  assert.equal(t.length, 3);
  assert.ok(t.every((tri) => area(tri.map((i) => p[i])) > 0));
  assert.equal(new Set(t.flat()).size, 5);
});

test('menos de 3 vértices lança erro', () => {
  assert.throws(() => triangula([[0, 0], [1, 1]]), RangeError);
});
