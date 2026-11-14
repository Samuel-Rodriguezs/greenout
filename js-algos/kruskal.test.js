import test from 'node:test';
import assert from 'node:assert/strict';
import { kruskal, UniaoBusca } from './kruskal.js';

test('união-busca', () => {
  const uf = new UniaoBusca(5);
  assert.equal(uf.unir(0, 1), true);
  assert.equal(uf.unir(1, 0), false);
  uf.unir(2, 3);
  assert.notEqual(uf.achar(0), uf.achar(2));
  uf.unir(1, 3);
  assert.equal(uf.achar(0), uf.achar(2));
  assert.equal(uf.conjuntos, 2);
});
test('AGM de grafo conhecido', () => {
  const arestas = [[0, 1, 4], [0, 2, 3], [1, 2, 1], [1, 3, 2], [2, 3, 4], [3, 4, 2], [4, 5, 6]];
  const r = kruskal(6, arestas);
  assert.equal(r.peso, 14);
  assert.equal(r.arestas.length, 5);
  assert.equal(r.conexo, true);
});
test('grafo desconexo gera floresta', () => {
  const r = kruskal(4, [[0, 1, 5], [2, 3, 1]]);
  assert.equal(r.conexo, false);
  assert.equal(r.peso, 6);
});
test('sem arestas e vértice único', () => {
  assert.deepEqual(kruskal(1, []), { arestas: [], peso: 0, conexo: true });
  assert.equal(kruskal(3, []).conexo, false);
});
test('ignora arestas que formam ciclo e laços', () => {
  const r = kruskal(3, [[0, 1, 1], [1, 2, 1], [0, 2, 1], [1, 1, 0]]);
  assert.equal(r.arestas.length, 2);
  assert.equal(r.peso, 2);
});
test('não altera a lista de arestas', () => {
  const a = [[0, 1, 9], [0, 1, 1]];
  kruskal(2, a);
  assert.deepEqual(a[0], [0, 1, 9]);
});
