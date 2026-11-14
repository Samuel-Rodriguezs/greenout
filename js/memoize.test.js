import { test } from 'node:test';
import assert from 'node:assert/strict';
import { memoize, memoizeAsync } from './memoize.js';

test('executa a função uma vez por conjunto de argumentos', () => {
  let chamadas = 0;
  const dobro = memoize((n) => { chamadas++; return n * 2; });
  assert.equal(dobro(2), 4);
  assert.equal(dobro(2), 4);
  assert.equal(dobro(3), 6);
  assert.equal(chamadas, 2);
});

test('cacheia resultados falsy (0, undefined)', () => {
  let chamadas = 0;
  const f = memoize(() => { chamadas++; return 0; });
  f(); f();
  assert.equal(chamadas, 1);
});

test('resolvedor de chave customizado', () => {
  let chamadas = 0;
  const f = memoize((a, b) => { chamadas++; return a + b; }, (a) => a);
  assert.equal(f(1, 2), 3);
  assert.equal(f(1, 100), 3); // mesma chave, resultado em cache
  assert.equal(chamadas, 1);
});

test('fibonacci memoizado recursivo', () => {
  const fib = memoize((n) => (n < 2 ? n : fib(n - 1) + fib(n - 2)));
  assert.equal(fib(80), 23416728348467685);
  assert.equal(fib.cache.size, 81);
});

test('memoizeAsync reutiliza a promessa em andamento', async () => {
  let chamadas = 0;
  const f = memoizeAsync(async (x) => { chamadas++; return x + 1; });
  const [a, b] = await Promise.all([f(1), f(1)]);
  assert.equal(a, 2);
  assert.equal(b, 2);
  assert.equal(chamadas, 1);
});

test('memoizeAsync não guarda rejeições', async () => {
  let chamadas = 0;
  const f = memoizeAsync(async () => {
    chamadas++;
    if (chamadas === 1) throw new Error('falha');
    return 'ok';
  });
  await assert.rejects(f(), /falha/);
  assert.equal(await f(), 'ok');
  assert.equal(chamadas, 2);
});
