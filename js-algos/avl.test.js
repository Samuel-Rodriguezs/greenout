import test from 'node:test';
import assert from 'node:assert/strict';
import { Avl } from './avl.js';

test('vazia', () => {
  const t = new Avl();
  assert.equal(t.tamanho, 0);
  assert.equal(t.altura, 0);
  assert.equal(t.minimo(), undefined);
  assert.equal(t.maximo(), undefined);
  assert.equal(t.remover(1), false);
  assert.equal(t.obter(1), undefined);
});
test('inserção ascendente permanece balanceada (log n)', () => {
  const t = new Avl();
  for (let i = 1; i <= 1023; i++) t.inserir(i);
  assert.equal(t.valida(), true);
  assert.equal(t.altura, 10);
  assert.equal(t.tamanho, 1023);
});
test('as quatro rotações', () => {
  for (const ordem of [[3, 2, 1], [1, 2, 3], [3, 1, 2], [1, 3, 2]]) {
    const t = new Avl();
    ordem.forEach((k) => t.inserir(k));
    assert.equal(t.altura, 2);
    assert.deepEqual([...t].map(([k]) => k), [1, 2, 3]);
  }
});
test('substitui valor de chave existente', () => {
  const t = new Avl().inserir('a', 1).inserir('a', 2);
  assert.equal(t.tamanho, 1);
  assert.equal(t.obter('a'), 2);
});
test('remoção mantém invariantes', () => {
  const t = new Avl();
  for (let i = 0; i < 200; i++) t.inserir(i);
  for (let i = 0; i < 200; i += 3) assert.equal(t.remover(i), true);
  t.valida();
  assert.equal(t.tem(3), false);
  assert.equal(t.tem(4), true);
  assert.equal(t.minimo()[0], 1);
  assert.equal(t.maximo()[0], 199);
  assert.equal(t.remover(3), false);
});
test('aleatório confere com Map', () => {
  const t = new Avl(), m = new Map();
  for (let i = 0; i < 3000; i++) {
    const k = Math.random() * 500 | 0;
    if (Math.random() < 0.6) { t.inserir(k, i); m.set(k, i); } else { assert.equal(t.remover(k), m.delete(k)); }
  }
  t.valida();
  assert.deepEqual([...t], [...m].sort((a, b) => a[0] - b[0]));
  assert.equal(t.tamanho, m.size);
});
test('remover tudo', () => {
  const t = new Avl();
  for (let i = 0; i < 50; i++) t.inserir(i);
  for (let i = 49; i >= 0; i--) t.remover(i);
  assert.equal(t.tamanho, 0);
  assert.equal(t.altura, 0);
});
