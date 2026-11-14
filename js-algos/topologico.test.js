import test from 'node:test';
import assert from 'node:assert/strict';
import { ordenacaoTopologica, ordemDeTarefas } from './topologico.js';

test('grafo vazio', () => assert.deepEqual(ordenacaoTopologica([]), []));
test('cadeia', () => assert.deepEqual(ordenacaoTopologica([[1], [2], []]), [0, 1, 2]));
test('diamante respeita dependências', () => {
  const ordem = ordenacaoTopologica([[1, 2], [3], [3], []]);
  assert.deepEqual(ordem, [0, 1, 2, 3]);
});
test('sem arestas: ordem por índice', () => {
  assert.deepEqual(ordenacaoTopologica([[], [], []]), [0, 1, 2]);
});
test('ciclo devolve null', () => {
  assert.equal(ordenacaoTopologica([[1], [0]]), null);
  assert.equal(ordenacaoTopologica([[0]]), null);
});
test('tarefas nomeadas', () => {
  const r = ordemDeTarefas({ app: ['lib', 'util'], lib: ['util'], teste: ['app'] });
  assert.deepEqual(r, ['util', 'lib', 'app', 'teste']);
});
test('tarefas com ciclo', () => {
  assert.equal(ordemDeTarefas({ a: ['b'], b: ['a'] }), null);
});
