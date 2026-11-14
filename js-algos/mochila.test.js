import test from 'node:test';
import assert from 'node:assert/strict';
import { mochila } from './mochila.js';

test('exemplo clássico', () => {
  const itens = [{ peso: 1, valor: 1 }, { peso: 3, valor: 4 }, { peso: 4, valor: 5 }, { peso: 5, valor: 7 }];
  const r = mochila(itens, 7);
  assert.equal(r.valor, 9);
  assert.equal(r.itens.reduce((s, i) => s + itens[i].peso, 0) <= 7, true);
  assert.equal(r.itens.reduce((s, i) => s + itens[i].valor, 0), 9);
});
test('sem itens ou capacidade zero', () => {
  assert.deepEqual(mochila([], 10), { valor: 0, itens: [] });
  assert.deepEqual(mochila([{ peso: 1, valor: 5 }], 0), { valor: 0, itens: [] });
});
test('item pesado demais', () => {
  assert.equal(mochila([{ peso: 10, valor: 100 }], 5).valor, 0);
});
test('cada item usado no máximo uma vez', () => {
  assert.equal(mochila([{ peso: 2, valor: 3 }], 10).valor, 3);
});
test('guloso falharia: prefere dois itens menores', () => {
  const itens = [{ peso: 10, valor: 60 }, { peso: 20, valor: 100 }, { peso: 30, valor: 120 }];
  const r = mochila(itens, 50);
  assert.equal(r.valor, 220);
  assert.deepEqual(r.itens, [1, 2]);
});
test('capacidade inválida', () => {
  assert.throws(() => mochila([], -1), RangeError);
  assert.throws(() => mochila([], 1.5), RangeError);
});
