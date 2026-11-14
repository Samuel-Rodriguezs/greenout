import { test } from 'node:test';
import assert from 'node:assert/strict';
import { pLimit } from './p-limit.js';

const dormir = (ms) => new Promise((r) => setTimeout(r, ms));

test('nunca excede o limite e mantém ordem dos resultados', async () => {
  const limite = pLimit(2);
  let ativos = 0, pico = 0;
  const tarefa = (i) => limite(async () => {
    ativos++; pico = Math.max(pico, ativos);
    await dormir(10);
    ativos--;
    return i;
  });
  const r = await Promise.all([0, 1, 2, 3, 4].map(tarefa));
  assert.deepEqual(r, [0, 1, 2, 3, 4]);
  assert.equal(pico, 2);
});
test('propaga erros e continua', async () => {
  const limite = pLimit(1);
  const a = limite(async () => { throw new Error('falhou'); });
  const b = limite(async () => 'ok');
  await assert.rejects(a, /falhou/);
  assert.equal(await b, 'ok');
});
test('valida concorrência', () => assert.throws(() => pLimit(0), RangeError));
