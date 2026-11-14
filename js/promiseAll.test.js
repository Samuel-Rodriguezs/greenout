import { test } from 'node:test';
import assert from 'node:assert/strict';
import { promiseAll, promiseAllSettled } from './promiseAll.js';

const atraso = (ms, v) => new Promise((r) => setTimeout(() => r(v), ms));

test('mantém a ordem independente do tempo de resolução', async () => {
  const r = await promiseAll([atraso(20, 'a'), atraso(1, 'b'), 'c']);
  assert.deepEqual(r, ['a', 'b', 'c']);
});

test('entrada vazia resolve com array vazio', async () => {
  assert.deepEqual(await promiseAll([]), []);
});

test('rejeita na primeira falha', async () => {
  const erro = new Error('falhou');
  await assert.rejects(promiseAll([atraso(10, 1), Promise.reject(erro)]), erro);
});

test('aceita iteráveis (Set)', async () => {
  assert.deepEqual(await promiseAll(new Set([1, 2])), [1, 2]);
});

test('promiseAllSettled reporta sucessos e falhas', async () => {
  const r = await promiseAllSettled([1, Promise.reject('x'), atraso(1, 3)]);
  assert.deepEqual(r, [
    { status: 'fulfilled', value: 1 },
    { status: 'rejected', reason: 'x' },
    { status: 'fulfilled', value: 3 },
  ]);
});
