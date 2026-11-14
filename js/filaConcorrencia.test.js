import { test } from 'node:test';
import assert from 'node:assert/strict';
import { FilaConcorrencia, mapearComLimite } from './filaConcorrencia.js';

const dormir = (ms) => new Promise((r) => setTimeout(r, ms));

test('nunca excede o limite de concorrência', async () => {
  const fila = new FilaConcorrencia(2);
  let ativas = 0;
  let maximo = 0;
  const tarefa = async () => {
    ativas++;
    maximo = Math.max(maximo, ativas);
    await dormir(5);
    ativas--;
  };
  await Promise.all(Array.from({ length: 7 }, () => fila.adicionar(tarefa)));
  assert.equal(maximo, 2);
});

test('devolve o resultado de cada tarefa', async () => {
  const fila = new FilaConcorrencia(3);
  const r = await Promise.all([1, 2, 3].map((n) => fila.adicionar(async () => n * 10)));
  assert.deepEqual(r, [10, 20, 30]);
});

test('respeita a ordem de entrada ao iniciar tarefas', async () => {
  const fila = new FilaConcorrencia(1);
  const ordem = [];
  await Promise.all([1, 2, 3].map((n) => fila.adicionar(async () => { ordem.push(n); await dormir(1); })));
  assert.deepEqual(ordem, [1, 2, 3]);
});

test('rejeição de uma tarefa não trava a fila', async () => {
  const fila = new FilaConcorrencia(1);
  const ruim = fila.adicionar(async () => { throw new Error('x'); });
  const boa = fila.adicionar(async () => 'ok');
  await assert.rejects(ruim, /x/);
  assert.equal(await boa, 'ok');
});

test('exceção síncrona na tarefa vira rejeição', async () => {
  const fila = new FilaConcorrencia(1);
  await assert.rejects(fila.adicionar(() => { throw new Error('sync'); }), /sync/);
  assert.equal(await fila.adicionar(() => 1), 1);
});

test('aguardarOciosa resolve ao esvaziar a fila', async () => {
  const fila = new FilaConcorrencia(2);
  await fila.aguardarOciosa(); // já ociosa
  let feitas = 0;
  for (let i = 0; i < 4; i++) fila.adicionar(async () => { await dormir(3); feitas++; });
  assert.equal(fila.ativas, 2);
  assert.equal(fila.pendentes, 2);
  await fila.aguardarOciosa();
  assert.equal(feitas, 4);
  assert.equal(fila.ativas, 0);
});

test('limite inválido', () => {
  assert.throws(() => new FilaConcorrencia(0), RangeError);
  assert.throws(() => new FilaConcorrencia(1.5), RangeError);
});

test('mapearComLimite mantém a ordem dos resultados', async () => {
  const r = await mapearComLimite([30, 1, 10], 2, async (ms, i) => { await dormir(ms); return `${i}:${ms}`; });
  assert.deepEqual(r, ['0:30', '1:1', '2:10']);
});
