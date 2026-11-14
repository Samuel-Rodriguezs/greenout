import test from 'node:test';
import assert from 'node:assert/strict';
import { KDTree } from './kdtree.js';

function lcg(semente) {
  let s = semente;
  return () => (s = (s * 1664525 + 1013904223) % 4294967296) / 4294967296;
}
const d2 = (a, b) => a.reduce((s, v, i) => s + (v - b[i]) ** 2, 0);

test('exemplo clássico da Wikipédia: vizinho de (9, 2) é (8, 1)', () => {
  const t = new KDTree([[2, 3], [5, 4], [9, 6], [4, 7], [8, 1], [7, 2]]);
  assert.deepEqual(t.maisProximo([9, 2]), [8, 1]);
  assert.equal(t.tamanho, 6);
});

test('vizinho mais próximo coincide com força bruta em 2D', () => {
  const r = lcg(1);
  const pts = Array.from({ length: 400 }, () => [r() * 1000, r() * 1000]);
  const t = new KDTree(pts);
  for (let i = 0; i < 40; i++) {
    const q = [r() * 1000, r() * 1000];
    const bruto = pts.reduce((m, p) => (d2(p, q) < d2(m, q) ? p : m));
    assert.deepEqual(t.maisProximo(q), bruto);
  }
});

test('funciona em 3D', () => {
  const r = lcg(9);
  const pts = Array.from({ length: 200 }, () => [r(), r(), r()]);
  const t = new KDTree(pts);
  const q = [0.5, 0.5, 0.5];
  const bruto = pts.reduce((m, p) => (d2(p, q) < d2(m, q) ? p : m));
  assert.deepEqual(t.maisProximo(q), bruto);
});

test('k mais próximos em ordem crescente de distância', () => {
  const r = lcg(3);
  const pts = Array.from({ length: 150 }, () => [r() * 50, r() * 50]);
  const t = new KDTree(pts);
  const q = [25, 25];
  const esperado = [...pts].sort((a, b) => d2(a, q) - d2(b, q)).slice(0, 5);
  assert.deepEqual(t.kMaisProximos(q, 5), esperado);
});

test('k maior que o tamanho devolve todos', () => {
  const t = new KDTree([[0, 0], [1, 1]]);
  assert.equal(t.kMaisProximos([0, 0], 10).length, 2);
});

test('busca por intervalo', () => {
  const t = new KDTree([[1, 1], [2, 5], [4, 4], [6, 2], [8, 8]]);
  const achados = t.buscaIntervalo([2, 2], [6, 5]).sort((a, b) => a[0] - b[0]);
  assert.deepEqual(achados, [[2, 5], [4, 4], [6, 2]]);
});

test('árvore vazia, k <= 0 e dimensões inconsistentes', () => {
  const vazia = new KDTree([]);
  assert.equal(vazia.maisProximo([1, 2]), null);
  assert.equal(vazia.tamanho, 0);
  assert.deepEqual(new KDTree([[1, 1]]).kMaisProximos([0, 0], 0), []);
  assert.throws(() => new KDTree([[1, 2], [1, 2, 3]]), RangeError);
  assert.throws(() => new KDTree([[1, 2]]).maisProximo([1]), RangeError);
});

test('pontos repetidos e entrada não modificada', () => {
  const entrada = [[3, 3], [1, 1], [3, 3], [2, 2]];
  const copia = entrada.map((p) => [...p]);
  const t = new KDTree(entrada);
  assert.deepEqual(entrada, copia);
  assert.equal(t.tamanho, 4);
  assert.deepEqual(t.maisProximo([3.1, 3.1]), [3, 3]);
});
