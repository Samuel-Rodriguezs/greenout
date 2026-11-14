import test from 'node:test';
import assert from 'node:assert/strict';
import { componentesFortes, pontesEArticulacoes } from './tarjan.js';

const ordena = (cs) => cs.map((c) => [...c]).sort((a, b) => a[0] - b[0]);

test('SCC: grafo vazio e vértice único', () => {
  assert.deepEqual(componentesFortes([]), []);
  assert.deepEqual(componentesFortes([[]]), [[0]]);
});
test('SCC: exemplo clássico', () => {
  const g = [[1], [2], [0, 3], [4], [5], [3], [5, 7], [6]];
  assert.deepEqual(ordena(componentesFortes(g)), [[0, 1, 2], [3, 4, 5], [6, 7]]);
});
test('SCC: DAG tem componentes unitárias', () => {
  assert.equal(componentesFortes([[1, 2], [3], [3], []]).length, 4);
});
test('SCC: laço próprio', () => {
  assert.deepEqual(componentesFortes([[0]]), [[0]]);
});
test('SCC: ordem topológica reversa (sumidouros primeiro)', () => {
  assert.deepEqual(componentesFortes([[1], []]), [[1], [0]]);
});
test('pontes e articulações', () => {
  // triângulo 0-1-2 ligado por 2-3 a 3-4
  const g = [[1, 2], [0, 2], [0, 1, 3], [2, 4], [3]];
  const r = pontesEArticulacoes(g);
  assert.deepEqual(r.pontes, [[2, 3], [3, 4]]);
  assert.deepEqual(r.articulacoes, [2, 3]);
});
test('ciclo não tem pontes nem articulações', () => {
  const r = pontesEArticulacoes([[1, 3], [0, 2], [1, 3], [2, 0]]);
  assert.deepEqual(r, { pontes: [], articulacoes: [] });
});
test('raiz com vários filhos é articulação', () => {
  assert.deepEqual(pontesEArticulacoes([[1, 2], [0], [0]]).articulacoes, [0]);
});
