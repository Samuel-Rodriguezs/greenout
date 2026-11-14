import test from 'node:test';
import assert from 'node:assert/strict';
import { createAutocomplete } from './autocomplete.js';

const tick = () => new Promise((r) => setImmediate(r));

test('debounce: só a última consulta é executada', async (t) => {
  t.mock.timers.enable({ apis: ['setTimeout'] });
  const calls = [];
  const ac = createAutocomplete(async (q) => { calls.push(q); return [q + '!']; }, { delay: 200 });
  ac.input('ab');
  t.mock.timers.tick(100);
  ac.input('abc');
  t.mock.timers.tick(199);
  assert.deepEqual(calls, []);
  t.mock.timers.tick(1);
  await tick();
  assert.deepEqual(calls, ['abc']);
  assert.deepEqual(ac.state.results, ['abc!']);
  assert.equal(ac.state.status, 'done');
});

test('abaixo do mínimo de caracteres limpa resultados', async (t) => {
  t.mock.timers.enable({ apis: ['setTimeout'] });
  const ac = createAutocomplete(async () => ['x'], { delay: 10, minChars: 3 });
  ac.input('abc');
  t.mock.timers.tick(10);
  await tick();
  assert.equal(ac.state.results.length, 1);
  ac.input('ab');
  assert.deepEqual(ac.state.results, []);
  assert.equal(ac.state.status, 'idle');
});

test('requisição anterior é cancelada via AbortSignal', async (t) => {
  t.mock.timers.enable({ apis: ['setTimeout'] });
  const signals = [];
  const resolvers = [];
  const ac = createAutocomplete(
    (q, { signal }) => { signals.push(signal); return new Promise((res) => resolvers.push(() => res([q]))); },
    { delay: 10 },
  );
  ac.input('aa');
  t.mock.timers.tick(10);
  ac.input('bb');
  assert.equal(signals[0].aborted, true);
  t.mock.timers.tick(10);
  resolvers[0]();
  await tick();
  assert.deepEqual(ac.state.results, []);
  resolvers[1]();
  await tick();
  assert.deepEqual(ac.state.results, ['bb']);
});

test('resposta obsoleta é ignorada mesmo sem abort cooperativo', async (t) => {
  t.mock.timers.enable({ apis: ['setTimeout'] });
  const pend = [];
  const ac = createAutocomplete((q) => new Promise((res) => pend.push([q, res])), { delay: 5 });
  ac.input('um');
  t.mock.timers.tick(5);
  ac.input('dois');
  t.mock.timers.tick(5);
  pend[1][1](['dois']);
  await tick();
  pend[0][1](['um']);
  await tick();
  assert.deepEqual(ac.state.results, ['dois']);
});

test('erros viram estado de erro', async (t) => {
  t.mock.timers.enable({ apis: ['setTimeout'] });
  const ac = createAutocomplete(async () => { throw new Error('falhou'); }, { delay: 1 });
  ac.input('ok');
  t.mock.timers.tick(1);
  await tick();
  assert.equal(ac.state.status, 'error');
  assert.equal(ac.state.error.message, 'falhou');
});

test('cancel interrompe o timer pendente', async (t) => {
  t.mock.timers.enable({ apis: ['setTimeout'] });
  let n = 0;
  const ac = createAutocomplete(async () => { n++; return []; }, { delay: 10 });
  ac.input('ok');
  ac.cancel();
  t.mock.timers.tick(50);
  await tick();
  assert.equal(n, 0);
});
