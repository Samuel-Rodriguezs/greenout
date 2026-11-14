import test from 'node:test';
import assert from 'node:assert/strict';
import { MaquinaEstados, criarSemaforo } from './maquinaEstados.js';

test('semáforo percorre o ciclo', () => {
  const s = criarSemaforo();
  const vistos = [s.estado];
  for (let i = 0; i < 3; i++) {
    s.enviar('PROXIMO');
    vistos.push(s.estado);
  }
  assert.deepEqual(vistos, ['vermelho', 'verde', 'amarelo', 'vermelho']);
  assert.equal(s.historico.length, 3);
});

test('evento inválido lança erro', () => {
  const s = criarSemaforo();
  assert.throws(() => s.enviar('QUEBRAR'), /inválido/);
});

test('configuração inválida', () => {
  assert.throws(() => new MaquinaEstados({ inicial: 'x', estados: {} }), /inicial/);
  assert.throws(
    () => new MaquinaEstados({ inicial: 'a', estados: { a: { on: { GO: 'b' } } } }),
    /inexistente/,
  );
});

test('guardas bloqueiam transições', () => {
  const m = new MaquinaEstados({
    inicial: 'fechada',
    estados: {
      fechada: { on: { ABRIR: { alvo: 'aberta', guarda: (c) => c.chave === true } } },
      aberta: {},
    },
  });
  assert.equal(m.pode('ABRIR', { chave: false }), false);
  assert.equal(m.enviar('ABRIR', { chave: false }), false);
  assert.equal(m.estado, 'fechada');
  assert.equal(m.enviar('ABRIR', { chave: true }), true);
  assert.equal(m.estado, 'aberta');
  assert.equal(m.estadoFinal(), true);
});

test('ordem de sair, ação, entrar e ouvintes', () => {
  const log = [];
  const m = new MaquinaEstados({
    inicial: 'a',
    estados: {
      a: { sair: () => log.push('sair a'), on: { IR: { alvo: 'b', acao: () => log.push('acao') } } },
      b: { entrar: () => log.push('entrar b') },
    },
  });
  const cancelar = m.aoMudar((de, para, ev) => log.push(`${de}>${para}:${ev}`));
  m.enviar('IR');
  assert.deepEqual(log, ['sair a', 'acao', 'entrar b', 'a>b:IR']);
  cancelar();
});
