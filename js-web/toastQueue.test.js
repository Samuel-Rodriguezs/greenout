import test from 'node:test';
import assert from 'node:assert/strict';
import { createToastQueue } from './toastQueue.js';

test('toast some após a duração', (t) => {
  t.mock.timers.enable({ apis: ['setTimeout'] });
  const q = createToastQueue({ duracao: 1000 });
  q.add('Salvo', { tipo: 'sucesso' });
  assert.equal(q.visiveis.length, 1);
  t.mock.timers.tick(999);
  assert.equal(q.visiveis.length, 1);
  t.mock.timers.tick(1);
  assert.equal(q.visiveis.length, 0);
});

test('limite de visíveis e promoção da fila', (t) => {
  t.mock.timers.enable({ apis: ['setTimeout'] });
  const q = createToastQueue({ maxVisiveis: 2, duracao: 1000 });
  q.add('a'); q.add('b'); q.add('c');
  assert.deepEqual(q.visiveis.map((x) => x.mensagem), ['a', 'b']);
  assert.equal(q.naEspera, 1);
  t.mock.timers.tick(1000);
  assert.deepEqual(q.visiveis.map((x) => x.mensagem), ['c']);
  assert.equal(q.naEspera, 0);
});

test('dismiss manual de visível e de item na espera', (t) => {
  t.mock.timers.enable({ apis: ['setTimeout'] });
  const q = createToastQueue({ maxVisiveis: 1 });
  const a = q.add('a');
  const b = q.add('b');
  assert.equal(q.dismiss(b), false);
  assert.equal(q.naEspera, 0);
  assert.equal(q.dismiss(a), true);
  assert.equal(q.visiveis.length, 0);
});

test('mensagens repetidas são agrupadas e renovam o tempo', (t) => {
  t.mock.timers.enable({ apis: ['setTimeout'] });
  const q = createToastQueue({ duracao: 1000 });
  q.add('Erro', { tipo: 'erro' });
  t.mock.timers.tick(800);
  q.add('Erro', { tipo: 'erro' });
  assert.equal(q.visiveis.length, 1);
  assert.equal(q.visiveis[0].contagem, 2);
  t.mock.timers.tick(800);
  assert.equal(q.visiveis.length, 1);
  t.mock.timers.tick(200);
  assert.equal(q.visiveis.length, 0);
});

test('duração 0 é persistente e onChange é chamado', (t) => {
  t.mock.timers.enable({ apis: ['setTimeout'] });
  const estados = [];
  const q = createToastQueue({ onChange: (s) => estados.push(s.visiveis.length) });
  q.add('fixo', { duracao: 0 });
  t.mock.timers.tick(100000);
  assert.equal(q.visiveis.length, 1);
  q.clear();
  assert.deepEqual(estados, [1, 0]);
});
