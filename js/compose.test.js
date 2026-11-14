import { test } from 'node:test';
import assert from 'node:assert/strict';
import { compose, pipe, pipeAsync } from './compose.js';

const mais1 = (x) => x + 1;
const dobro = (x) => x * 2;

test('pipe aplica da esquerda para a direita', () => {
  assert.equal(pipe(mais1, dobro)(3), 8);
});

test('compose aplica da direita para a esquerda', () => {
  assert.equal(compose(mais1, dobro)(3), 7);
});

test('a primeira função pode receber vários argumentos', () => {
  assert.equal(pipe((a, b) => a + b, dobro)(1, 2), 6);
});

test('sem funções devolve o primeiro argumento', () => {
  assert.equal(pipe()(5), 5);
  assert.equal(compose()('x'), 'x');
});

test('compose não altera o array original de funções', () => {
  const fns = [mais1, dobro];
  compose(...fns);
  assert.deepEqual(fns, [mais1, dobro]);
});

test('rejeita argumentos que não são funções', () => {
  assert.throws(() => pipe(mais1, 3), TypeError);
  assert.throws(() => compose('x'), TypeError);
});

test('pipeAsync mistura funções síncronas e assíncronas', async () => {
  const f = pipeAsync(async (x) => x + 1, dobro, async (x) => `r=${x}`);
  assert.equal(await f(1), 'r=4');
});

test('pipeAsync propaga erros', async () => {
  const f = pipeAsync(async () => { throw new Error('boom'); }, dobro);
  await assert.rejects(f(), /boom/);
});
