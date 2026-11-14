import test from 'node:test';
import assert from 'node:assert/strict';
import { bfs, dfs, menorCaminho, componentes, temCiclo } from './travessiaGrafo.js';

const g = [[1, 2], [3], [3, 4], [5], [5], []];

test('bfs por níveis', () => assert.deepEqual(bfs(g, 0), [0, 1, 2, 3, 4, 5]));
test('dfs em profundidade', () => assert.deepEqual(dfs(g, 0), [0, 1, 3, 5, 2, 4]));
test('vértice isolado', () => {
  assert.deepEqual(bfs([[]], 0), [0]);
  assert.deepEqual(dfs([[]], 0), [0]);
});
test('menor caminho', () => {
  assert.deepEqual(menorCaminho(g, 0, 5), [0, 1, 3, 5]);
  assert.deepEqual(menorCaminho(g, 0, 0), [0]);
  assert.equal(menorCaminho(g, 5, 0), null);
});
test('componentes conexas', () => {
  const nd = [[1], [0], [3], [2], []];
  assert.deepEqual(componentes(nd), [[0, 1], [2, 3], [4]]);
});
test('detecção de ciclo', () => {
  assert.equal(temCiclo(g), false);
  assert.equal(temCiclo([[1], [2], [0]]), true);
  assert.equal(temCiclo([[0]]), true);
  assert.equal(temCiclo([]), false);
});
test('grafo com ciclo não trava a travessia', () => {
  assert.deepEqual(bfs([[1], [0, 2], [1]], 0), [0, 1, 2]);
  assert.deepEqual(dfs([[1], [0, 2], [1]], 0), [0, 1, 2]);
});
