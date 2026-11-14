import test from 'node:test';
import assert from 'node:assert/strict';
import { createOfflineQueue } from './filaOffline.js';

let seq = 0;
const gerarId = () => `id${++seq}`;

test('offline acumula e online sincroniza em ordem', async () => {
  const enviados = [];
  const q = createOfflineQueue({ send: async (p) => { enviados.push(p); }, online: false, gerarId });
  await q.enqueue('a');
  await q.enqueue('b');
  assert.equal(q.pendentes, 2);
  assert.deepEqual(enviados, []);
  const r = await q.setOnline(true);
  assert.deepEqual(r, { enviados: 2, descartados: 0, pendentes: 0 });
  assert.deepEqual(enviados, ['a', 'b']);
});

test('online envia imediatamente', async () => {
  const enviados = [];
  const q = createOfflineQueue({ send: async (p) => { enviados.push(p); }, gerarId });
  await q.enqueue({ x: 1 });
  assert.deepEqual(enviados, [{ x: 1 }]);
  assert.equal(q.pendentes, 0);
});

test('falha temporária mantém a ordem e tenta de novo', async () => {
  const enviados = [];
  let falhas = 1;
  const q = createOfflineQueue({
    send: async (p) => { if (p === 'a' && falhas-- > 0) throw new Error('rede'); enviados.push(p); },
    online: false, gerarId,
  });
  await q.enqueue('a');
  await q.enqueue('b');
  let r = await q.setOnline(true);
  assert.deepEqual(r, { enviados: 0, descartados: 0, pendentes: 2 });
  assert.equal(q.list()[0].tentativas, 1);
  r = await q.sync();
  assert.deepEqual(enviados, ['a', 'b']);
  assert.equal(r.pendentes, 0);
});

test('descarta após exceder tentativas e com erro permanente', async () => {
  const eventos = [];
  const q = createOfflineQueue({
    send: async (p) => { if (p === 'ruim') throw Object.assign(new Error('400'), { permanent: true }); throw new Error('rede'); },
    maxTentativas: 2, online: false, gerarId,
  });
  q.subscribe((e) => eventos.push(e.type));
  await q.enqueue('ruim');
  let r = await q.setOnline(true);
  assert.equal(r.descartados, 1);
  await q.setOnline(false);
  await q.enqueue('t');
  await q.setOnline(true);
  r = await q.sync();
  assert.equal(r.descartados, 1);
  assert.equal(q.pendentes, 0);
  assert.ok(eventos.includes('dropped') && eventos.includes('retry'));
});

test('persistência: nova instância recupera a fila', async () => {
  const storage = new Map();
  const a = createOfflineQueue({ send: async () => {}, storage, online: false, gerarId });
  await a.enqueue('persistido');
  const enviados = [];
  const b = createOfflineQueue({ send: async (p) => { enviados.push(p); }, storage, online: false, gerarId });
  assert.equal(b.pendentes, 1);
  await b.setOnline(true);
  assert.deepEqual(enviados, ['persistido']);
});

test('sync concorrente reaproveita a mesma execução', async () => {
  let n = 0;
  const q = createOfflineQueue({ send: async () => { n++; }, online: false, gerarId });
  await q.enqueue(1);
  q.setOnline(true);
  const [r1, r2] = await Promise.all([q.sync(), q.sync()]);
  assert.equal(r1, r2);
  assert.equal(n, 1);
});
