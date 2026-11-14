import test from 'node:test';
import assert from 'node:assert/strict';
import { TodoList } from './todoList.js';

test('adiciona e ordena por prioridade', () => {
  const l = new TodoList();
  l.adicionar('baixa', { prioridade: 'baixa' });
  l.adicionar('alta', { prioridade: 'alta' });
  l.adicionar('media');
  assert.deepEqual(l.listar().map((t) => t.titulo), ['alta', 'media', 'baixa']);
});

test('concluir, filtrar e resumo', () => {
  const l = new TodoList();
  const a = l.adicionar('a');
  l.adicionar('b');
  l.concluir(a.id);
  assert.equal(l.listar({ concluidas: true }).length, 1);
  assert.deepEqual(l.resumo(), { total: 2, feitas: 1, pendentes: 1, percentual: 50 });
  l.concluir(a.id, false);
  assert.equal(l.resumo().feitas, 0);
});

test('remover e editar', () => {
  const l = new TodoList();
  const a = l.adicionar('a');
  l.editar(a.id, '  novo  ');
  assert.equal(l.listar()[0].titulo, 'novo');
  l.remover(a.id);
  assert.equal(l.listar().length, 0);
  assert.throws(() => l.remover(a.id), /não encontrada/);
});

test('atrasadas', () => {
  const l = new TodoList();
  l.adicionar('velha', { vencimento: '2024-01-01' });
  l.adicionar('futura', { vencimento: '2030-01-01' });
  const feita = l.adicionar('feita', { vencimento: '2024-01-01' });
  l.concluir(feita.id);
  assert.deepEqual(l.atrasadas('2025-01-01').map((t) => t.titulo), ['velha']);
});

test('serializa e restaura mantendo ids', () => {
  const l = new TodoList();
  l.adicionar('x', { prioridade: 'alta' });
  const c = l.adicionar('y');
  l.concluir(c.id);
  const copia = TodoList.desserializar(l.serializar());
  assert.deepEqual(copia.listar(), l.listar());
  assert.equal(copia.adicionar('z').id, 3);
});

test('validações e entradas corrompidas', () => {
  const l = new TodoList();
  assert.throws(() => l.adicionar('  '), /obrigatório/);
  assert.throws(() => l.adicionar('a', { prioridade: 'urgente' }), /inválida/);
  assert.throws(() => TodoList.desserializar('{'), /JSON inválido/);
  assert.throws(() => TodoList.desserializar('{"versao":2}'), /não suportado/);
  assert.throws(
    () => TodoList.desserializar('{"versao":1,"proximoId":2,"tarefas":[{"titulo":"a","prioridade":"x"}]}'),
    /corrompida/,
  );
});
