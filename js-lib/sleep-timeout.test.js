import { test } from 'node:test';
import assert from 'node:assert/strict';
import { sleep, comTimeout, TimeoutError } from './sleep-timeout.js';

test('sleep espera pelo menos o tempo', async () => {
  const t = Date.now();
  await sleep(30);
  assert.ok(Date.now() - t >= 25);
});
test('comTimeout resolve se rápido', async () => {
  assert.equal(await comTimeout(sleep(5).then(() => 'ok'), 200), 'ok');
});
test('comTimeout rejeita se lento', async () => {
  await assert.rejects(comTimeout(sleep(200), 10), TimeoutError);
});
