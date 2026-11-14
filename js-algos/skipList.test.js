import test from 'node:test';
import assert from 'node:assert/strict';
import { SkipList } from './skipList.js';

test('vazia', () => {
  const s = new SkipList();
  assert.equal(s.tamanho, 0);
  assert.equal(s.obter(1), undefined);
  assert.equal(s.remover(1), false);
  assert.deepEqual([...s], []);
});
test('inserção mantém ordem e sobrescreve', () => {
  const s = new SkipList();
  [5, 1, 3, 9, 7, 3].forEach((k) => s.definir(k, `v${k}`));
  assert.deepEqual([...s].map(([k]) => k), [1, 3, 5, 7, 9]);
  s.definir(3, 'novo');
  assert.equal(s.obter(3), 'novo');
  assert.equal(s.tamanho, 5);
});
test('remoção', () => {
  const s = new SkipList();
  for (let i = 0; i < 20; i++) s.definir(i, i);
  for (let i = 0; i < 20; i += 2) assert.equal(s.remover(i), true);
  assert.equal(s.tamanho, 10);
  assert.equal(s.tem(4), false);
  assert.equal(s.tem(5), true);
  assert.equal(s.remover(4), false);
});
test('faixa e lower bound', () => {
  const s = new SkipList();
  for (const k of [10, 20, 30, 40, 50]) s.definir(k, k);
  assert.deepEqual([...s.faixa(20, 50)].map(([k]) => k), [20, 30, 40]);
  assert.deepEqual(s.primeiroMaiorOuIgual(25), [30, 30]);
  assert.equal(s.primeiroMaiorOuIgual(51), undefined);
});
test('determinístico com rand injetado (níveis máximos e mínimos)', () => {
  for (const rand of [() => 0, () => 0.99]) {
    const s = new SkipList({ rand, nivelMax: 4 });
    for (let i = 0; i < 30; i++) s.definir((i * 7) % 30, i);
    assert.deepEqual([...s].map(([k]) => k), Array.from({ length: 30 }, (_, i) => i));
    for (let i = 0; i < 30; i++) s.remover(i);
    assert.equal(s.tamanho, 0);
  }
});
test('aleatório confere com Map ordenado', () => {
  const s = new SkipList(), m = new Map();
  for (let i = 0; i < 2000; i++) {
    const k = Math.random() * 300 | 0;
    if (Math.random() < 0.6) { s.definir(k, i); m.set(k, i); }
    else { assert.equal(s.remover(k), m.delete(k)); }
  }
  assert.deepEqual([...s], [...m].sort((a, b) => a[0] - b[0]));
  assert.equal(s.tamanho, m.size);
});
test('comparador customizado (strings por tamanho)', () => {
  const s = new SkipList({ cmp: (a, b) => a.length - b.length });
  s.definir('ccc', 3).definir('a', 1).definir('bb', 2);
  assert.deepEqual([...s].map(([k]) => k), ['a', 'bb', 'ccc']);
});
