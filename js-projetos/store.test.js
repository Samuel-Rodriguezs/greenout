import test from 'node:test';
import assert from 'node:assert/strict';
import { criarStore, combinarReducers, loggerMiddleware } from './store.js';

const contador = (estado = 0, acao) => {
  if (acao.tipo === 'INC') return estado + 1;
  if (acao.tipo === 'ADD') return estado + acao.valor;
  return estado;
};

test('estado inicial e dispatch', () => {
  const s = criarStore(contador, 5);
  assert.equal(s.getState(), 5);
  s.dispatch({ tipo: 'INC' });
  s.dispatch({ tipo: 'ADD', valor: 10 });
  assert.equal(s.getState(), 16);
});

test('subscribe notifica e unsubscribe cancela', () => {
  const s = criarStore(contador, 0);
  let chamadas = 0;
  const cancelar = s.subscribe(() => chamadas++);
  s.dispatch({ tipo: 'INC' });
  cancelar();
  cancelar();
  s.dispatch({ tipo: 'INC' });
  assert.equal(chamadas, 1);
});

test('valida ação e reducer', () => {
  const s = criarStore(contador, 0);
  assert.throws(() => s.dispatch({}), TypeError);
  assert.throws(() => s.dispatch(null), TypeError);
  assert.throws(() => criarStore(null), TypeError);
});

test('reducer não pode despachar', () => {
  let s;
  const ruim = (e = 0, a) => {
    if (a.tipo === 'X') s.dispatch({ tipo: 'Y' });
    return e;
  };
  s = criarStore(ruim);
  assert.throws(() => s.dispatch({ tipo: 'X' }), /Reducers não podem/);
});

test('combinarReducers preserva referência quando nada muda', () => {
  const raiz = combinarReducers({ a: contador, b: (e = 'x') => e });
  const s = criarStore(raiz);
  const antes = s.getState();
  s.dispatch({ tipo: 'NADA' });
  assert.equal(s.getState(), antes);
  s.dispatch({ tipo: 'INC' });
  assert.deepEqual(s.getState(), { a: 1, b: 'x' });
});

test('middleware logger registra antes e depois', () => {
  const logs = [];
  const s = criarStore(contador, 0, loggerMiddleware((l) => logs.push(l)));
  s.dispatch({ tipo: 'INC' });
  assert.equal(logs.length, 1);
  assert.equal(logs[0].antes, 0);
  assert.equal(logs[0].depois, 1);
});
