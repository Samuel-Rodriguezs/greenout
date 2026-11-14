import test from 'node:test';
import assert from 'node:assert/strict';
import { createSWRCache } from './cacheSWR.js';

function setup(opts = {}) {
  let t = 0;
  let n = 0;
  const fetcher = async (k) => `${k}#${++n}`;
  const cache = createSWRCache(fetcher, { ttl: 1000, staleTtl: 5000, agora: () => t, ...opts });
  return { cache, avancar: (ms) => { t += ms; }, chamadas: () => n };
}

test('miss busca e depois fica fresh', async () => {
  const { cache, chamadas } = setup();
  assert.deepEqual(await cache.get('a'), { value: 'a#1', status: 'miss' });
  assert.deepEqual(await cache.get('a'), { value: 'a#1', status: 'fresh' });
  assert.equal(chamadas(), 1);
});

test('stale devolve valor antigo e revalida em segundo plano', async () => {
  const { cache, avancar } = setup();
  await cache.get('a');
  avancar(2000);
  const r = await cache.get('a');
  assert.equal(r.status, 'stale');
  assert.equal(r.value, 'a#1');
  assert.equal(await r.revalidating, 'a#2');
  assert.deepEqual(await cache.get('a'), { value: 'a#2', status: 'fresh' });
});

test('requisições simultâneas são deduplicadas', async () => {
  const { cache, chamadas } = setup();
  const [x, y] = await Promise.all([cache.get('k'), cache.get('k')]);
  assert.equal(x.value, y.value);
  assert.equal(chamadas(), 1);
});

test('expirado além do staleTtl vira miss', async () => {
  const { cache, avancar } = setup();
  await cache.get('a');
  avancar(6000);
  assert.equal((await cache.get('a')).status, 'miss');
});

test('falha na revalidação mantém o valor stale', async () => {
  let t = 0;
  let falhar = false;
  const cache = createSWRCache(async () => { if (falhar) throw new Error('rede'); return 'ok'; }, { ttl: 10, staleTtl: 1000, agora: () => t });
  await cache.get('a');
  t = 50;
  falhar = true;
  const r = await cache.get('a');
  assert.equal(r.value, 'ok');
  await assert.rejects(r.revalidating, /rede/);
  assert.equal(cache.peek('a'), 'ok');
});

test('miss com erro propaga e não cacheia', async () => {
  const cache = createSWRCache(async () => { throw new Error('x'); });
  await assert.rejects(cache.get('a'), /x/);
  assert.equal(cache.size, 0);
});

test('invalidate, set e clear', async () => {
  const { cache } = setup();
  cache.set('a', 'manual');
  assert.equal((await cache.get('a')).value, 'manual');
  cache.invalidate('a');
  assert.equal((await cache.get('a')).status, 'miss');
  cache.clear();
  assert.equal(cache.size, 0);
});
