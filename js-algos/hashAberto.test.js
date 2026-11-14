import test from 'node:test';
import assert from 'node:assert/strict';
import { HashAberto, hashFnv } from './hashAberto.js';

test('hash determinístico e distingue tipos', () => {
  assert.equal(hashFnv('abc'), hashFnv('abc'));
  assert.notEqual(hashFnv('abc'), hashFnv('abd'));
  assert.notEqual(hashFnv(1), hashFnv('1'));
});
test('definir, obter e sobrescrever', () => {
  const h = new HashAberto();
  h.definir('a', 1).definir('b', 2);
  assert.equal(h.obter('a'), 1);
  h.definir('a', 9);
  assert.equal(h.obter('a'), 9);
  assert.equal(h.tamanho, 2);
  assert.equal(h.obter('zzz'), undefined);
  assert.equal(h.tem('b'), true);
  assert.equal(h.tem('c'), false);
});
test('crescimento mantém todos os itens', () => {
  const h = new HashAberto(4);
  for (let i = 0; i < 1000; i++) h.definir(`k${i}`, i);
  assert.equal(h.tamanho, 1000);
  assert.ok(h.capacidade >= 1000);
  for (let i = 0; i < 1000; i++) assert.equal(h.obter(`k${i}`), i);
});
test('remoção não quebra a sondagem (lápide)', () => {
  const colide = new HashAberto(8, () => 0); // todas as chaves colidem
  colide.definir('a', 1).definir('b', 2).definir('c', 3);
  assert.equal(colide.remover('a'), true);
  assert.equal(colide.obter('c'), 3);
  assert.equal(colide.remover('a'), false);
  colide.definir('d', 4);
  assert.deepEqual([...colide].map(([k]) => k).sort(), ['b', 'c', 'd']);
});
test('chaves de vários tipos', () => {
  const h = new HashAberto();
  h.definir(1, 'num').definir('1', 'str').definir(NaN, 'nan').definir(null, 'nulo');
  assert.equal(h.obter(1), 'num');
  assert.equal(h.obter('1'), 'str');
  assert.equal(h.obter(NaN), 'nan');
  assert.equal(h.obter(null), 'nulo');
});
test('muitas inserções e remoções alternadas', () => {
  const h = new HashAberto(4);
  for (let r = 0; r < 20; r++) {
    for (let i = 0; i < 50; i++) h.definir(i, r);
    for (let i = 0; i < 50; i += 2) h.remover(i);
  }
  assert.equal(h.tamanho, 25);
  for (let i = 1; i < 50; i += 2) assert.equal(h.obter(i), 19);
  for (let i = 0; i < 50; i += 2) assert.equal(h.tem(i), false);
});
