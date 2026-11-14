import test, { mock } from 'node:test';
import assert from 'node:assert/strict';
import { Cronometro, contagemRegressiva, formatarTempo } from './cronometro.js';

test('formatarTempo', () => {
  assert.equal(formatarTempo(0), '00:00:00');
  assert.equal(formatarTempo(61_999), '00:01:01');
  assert.equal(formatarTempo(3_725_000), '01:02:05');
});

test('cronômetro mede o tempo com timers falsos', (t) => {
  t.mock.timers.enable({ apis: ['setInterval', 'Date'], now: 1000 });
  const ticks = [];
  const c = new Cronometro({ aoTick: (ms) => ticks.push(ms) });
  c.iniciar();
  for (let k = 0; k < 3; k++) t.mock.timers.tick(1000);
  assert.equal(c.decorrido, 3000);
  assert.deepEqual(ticks, [1000, 2000, 3000]);
  c.pausar();
  t.mock.timers.tick(5000);
  assert.equal(c.decorrido, 3000);
  c.iniciar();
  t.mock.timers.tick(2000);
  assert.equal(c.decorrido, 5000);
  c.pausar();
});

test('voltas registram parcial e total', (t) => {
  t.mock.timers.enable({ apis: ['setInterval', 'Date'], now: 0 });
  const c = new Cronometro();
  c.iniciar();
  t.mock.timers.tick(1500);
  c.volta();
  t.mock.timers.tick(2500);
  c.volta();
  assert.deepEqual(c.voltas, [
    { numero: 1, total: 1500, parcial: 1500 },
    { numero: 2, total: 4000, parcial: 2500 },
  ]);
  c.zerar();
  assert.equal(c.decorrido, 0);
  assert.equal(c.rodando, false);
  assert.equal(c.voltas.length, 0);
});

test('estados inválidos', () => {
  const c = new Cronometro();
  assert.throws(() => c.pausar(), /não está rodando/);
  c.iniciar();
  assert.throws(() => c.iniciar(), /já está rodando/);
  c.pausar();
});

test('contagem regressiva dispara aoFim uma vez', (t) => {
  t.mock.timers.enable({ apis: ['setInterval', 'Date'], now: 0 });
  const ticks = [];
  const fim = mock.fn();
  contagemRegressiva(3000, { aoTick: (r) => ticks.push(r), aoFim: fim });
  for (let k = 0; k < 10; k++) t.mock.timers.tick(1000);
  assert.deepEqual(ticks, [2000, 1000, 0]);
  assert.equal(fim.mock.callCount(), 1);
});

test('contagem regressiva pode ser cancelada e valida duração', (t) => {
  t.mock.timers.enable({ apis: ['setInterval', 'Date'], now: 0 });
  const fim = mock.fn();
  const cancelar = contagemRegressiva(5000, { aoFim: fim });
  t.mock.timers.tick(2000);
  cancelar();
  t.mock.timers.tick(10_000);
  assert.equal(fim.mock.callCount(), 0);
  assert.throws(() => contagemRegressiva(0), RangeError);
});
