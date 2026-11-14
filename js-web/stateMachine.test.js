import test from 'node:test';
import assert from 'node:assert/strict';
import { createMachine } from './stateMachine.js';

const log = [];
const machine = createMachine({
  initial: 'idle',
  context: { tentativas: 0 },
  states: {
    idle: { on: { FETCH: 'loading' }, entry: () => { log.push('entra idle'); } },
    loading: {
      entry: () => { log.push('entra loading'); },
      exit: () => { log.push('sai loading'); },
      on: {
        OK: 'sucesso',
        FALHA: [
          { guard: (c) => c.tentativas >= 2, target: 'erro' },
          { target: 'idle', actions: (c) => ({ tentativas: c.tentativas + 1 }) },
        ],
      },
    },
    sucesso: {},
    erro: { on: { RESET: { target: 'idle', actions: () => ({ tentativas: 0 }) } } },
  },
});

test('estado inicial e entry', () => {
  assert.equal(machine.initialState.value, 'idle');
  assert.ok(log.includes('entra idle'));
});

test('transições simples e entry/exit', () => {
  log.length = 0;
  const s = machine.interpret();
  s.send('FETCH');
  assert.equal(s.state.value, 'loading');
  s.send({ type: 'OK' });
  assert.equal(s.state.value, 'sucesso');
  assert.deepEqual(log, ['entra loading', 'sai loading']);
});

test('guardas escolhem a transição', () => {
  const s = machine.interpret();
  for (let i = 0; i < 2; i++) { s.send('FETCH'); s.send('FALHA'); }
  assert.equal(s.state.value, 'idle');
  assert.equal(s.state.context.tentativas, 2);
  s.send('FETCH');
  s.send('FALHA');
  assert.equal(s.state.value, 'erro');
  s.send('RESET');
  assert.deepEqual([s.state.value, s.state.context.tentativas], ['idle', 0]);
});

test('eventos inválidos são ignorados', () => {
  const s = machine.interpret();
  const antes = s.state;
  s.send('OK');
  assert.equal(s.state, antes);
  assert.equal(s.can('OK'), false);
  assert.equal(s.can('FETCH'), true);
});

test('subscribe notifica mudanças', () => {
  const s = machine.interpret();
  const vistos = [];
  const off = s.subscribe((st) => vistos.push(st.value));
  s.send('FETCH');
  off();
  s.send('OK');
  assert.deepEqual(vistos, ['loading']);
});

test('configuração inválida', () => {
  assert.throws(() => createMachine({ initial: 'x', states: {} }), /inexistente/);
  const m = createMachine({ initial: 'a', states: { a: { on: { GO: 'zzz' } } } });
  assert.throws(() => m.interpret().send('GO'), /desconhecido/);
});
