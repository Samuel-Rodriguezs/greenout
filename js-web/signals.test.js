import test from 'node:test';
import assert from 'node:assert/strict';
import { signal, computed, effect, batch } from './signals.js';

test('signal lê e escreve', () => {
  const a = signal(1);
  assert.equal(a(), 1);
  a.set(2);
  assert.equal(a(), 2);
  a.update((x) => x * 5);
  assert.equal(a.peek(), 10);
});

test('effect reexecuta ao mudar dependência', () => {
  const a = signal(1);
  const log = [];
  effect(() => { log.push(a()); });
  a.set(2);
  a.set(2);
  a.set(3);
  assert.deepEqual(log, [1, 2, 3]);
});

test('computed deriva e atualiza', () => {
  const a = signal(2);
  const b = signal(3);
  const soma = computed(() => a() + b());
  assert.equal(soma(), 5);
  a.set(10);
  assert.equal(soma(), 13);
});

test('computed encadeado em effect', () => {
  const a = signal(1);
  const dobro = computed(() => a() * 2);
  const vistos = [];
  effect(() => { vistos.push(dobro()); });
  a.set(4);
  assert.deepEqual(vistos, [2, 8]);
});

test('dispose para o effect e roda cleanup', () => {
  const a = signal(0);
  let runs = 0, cleanups = 0;
  const stop = effect(() => { a(); runs++; return () => { cleanups++; }; });
  a.set(1);
  assert.equal(runs, 2);
  assert.equal(cleanups, 1);
  stop();
  assert.equal(cleanups, 2);
  a.set(2);
  assert.equal(runs, 2);
});

test('batch agrupa notificações', () => {
  const a = signal(1);
  const b = signal(1);
  let runs = 0;
  effect(() => { a(); b(); runs++; });
  batch(() => { a.set(2); b.set(2); });
  assert.equal(runs, 2);
});

test('dependências dinâmicas', () => {
  const flag = signal(true);
  const x = signal('x');
  const y = signal('y');
  const log = [];
  effect(() => { log.push(flag() ? x() : y()); });
  y.set('y2');
  assert.deepEqual(log, ['x']);
  flag.set(false);
  assert.deepEqual(log, ['x', 'y2']);
  x.set('x2');
  assert.equal(log.length, 2);
});
