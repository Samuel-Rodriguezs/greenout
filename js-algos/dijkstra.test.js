import test from 'node:test';
import assert from 'node:assert/strict';
import { dijkstra, caminhoMinimo } from './dijkstra.js';

const g = [
  [[1, 7], [2, 9], [5, 14]],
  [[0, 7], [2, 10], [3, 15]],
  [[0, 9], [1, 10], [3, 11], [5, 2]],
  [[1, 15], [2, 11], [4, 6]],
  [[3, 6], [5, 9]],
  [[0, 14], [2, 2], [4, 9]],
];

test('distâncias clássicas', () => {
  assert.deepEqual(dijkstra(g, 0).dist, [0, 7, 9, 20, 20, 11]);
});
test('reconstrói caminho', () => {
  assert.deepEqual(caminhoMinimo(g, 0, 4), { custo: 20, caminho: [0, 2, 5, 4] });
});
test('origem igual ao destino', () => {
  assert.deepEqual(caminhoMinimo(g, 3, 3), { custo: 0, caminho: [3] });
});
test('inalcançável', () => {
  const h = [[[1, 1]], [], []];
  assert.equal(dijkstra(h, 0).dist[2], Infinity);
  assert.equal(caminhoMinimo(h, 0, 2), null);
});
test('arestas com peso zero', () => {
  assert.deepEqual(dijkstra([[[1, 0]], [[2, 0]], []], 0).dist, [0, 0, 0]);
});
test('peso negativo rejeitado', () => {
  assert.throws(() => dijkstra([[[1, -1]], []], 0), RangeError);
});
