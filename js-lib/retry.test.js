import { test } from 'node:test';
import assert from 'node:assert/strict';
import { retry } from './retry.js';

test('sucesso após falhas, com backoff', async () => {
  const esperas = [];
  let n = 0;
  const r = await retry(async () => { if (++n < 3) throw new Error('x'); return 'ok'; },
    { base: 10, esperar: async (ms) => esperas.push(ms) });
  assert.equal(r, 'ok');
  assert.deepEqual(esperas, [10, 20]);
});
test('lança o último erro ao esgotar', async () => {
  let n = 0;
  await assert.rejects(retry(async () => { throw new Error('e' + ++n); }, { tentativas: 2, esperar: async () => {} }), /e2/);
});
test('respeita o teto max', async () => {
  const esperas = [];
  await assert.rejects(retry(async () => { throw new Error('x'); }, { tentativas: 4, base: 100, max: 150, esperar: async (ms) => esperas.push(ms) }));
  assert.deepEqual(esperas, [100, 150, 150]);
});
