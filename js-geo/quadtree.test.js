import test from 'node:test';
import assert from 'node:assert/strict';
import { QuadTree } from './quadtree.js';
import { criaBBox } from './bbox.js';

// Gerador pseudoaleatório determinístico (LCG)
function lcg(semente) {
  let s = semente;
  return () => (s = (s * 1664525 + 1013904223) % 4294967296) / 4294967296;
}

const caixa = criaBBox(0, 0, 100, 100);

test('insere e conta; rejeita ponto fora dos limites', () => {
  const q = new QuadTree(caixa);
  assert.equal(q.insere({ x: 10, y: 10 }), true);
  assert.equal(q.insere({ x: 101, y: 10 }), false);
  assert.equal(q.tamanho, 1);
});

test('subdivide ao passar da capacidade mantendo todos os pontos', () => {
  const q = new QuadTree(caixa, { capacidade: 2 });
  for (let i = 0; i < 20; i++) q.insere({ x: i * 5, y: i * 4, dados: i });
  assert.equal(q.tamanho, 20);
  assert.equal(q.buscaRetangulo(caixa).length, 20);
});

test('busca por retângulo coincide com varredura linear', () => {
  const r = lcg(42);
  const todos = Array.from({ length: 500 }, () => ({ x: r() * 100, y: r() * 100 }));
  const q = new QuadTree(caixa);
  todos.forEach((p) => q.insere(p));
  const area = criaBBox(20, 30, 55, 70);
  const esperado = todos.filter((p) => p.x >= 20 && p.x <= 55 && p.y >= 30 && p.y <= 70);
  const achado = q.buscaRetangulo(area);
  assert.equal(achado.length, esperado.length);
  assert.deepEqual(new Set(achado), new Set(esperado));
});

test('busca por raio', () => {
  const q = new QuadTree(caixa);
  [[50, 50], [53, 54], [60, 60], [10, 10]].forEach(([x, y]) => q.insere({ x, y }));
  const r = q.buscaRaio(50, 50, 5);
  assert.deepEqual(r.map((p) => [p.x, p.y]).sort(), [[50, 50], [53, 54]]);
});

test('vizinho mais próximo coincide com força bruta', () => {
  const r = lcg(7);
  const todos = Array.from({ length: 300 }, () => ({ x: r() * 100, y: r() * 100 }));
  const q = new QuadTree(caixa);
  todos.forEach((p) => q.insere(p));
  for (let i = 0; i < 25; i++) {
    const [x, y] = [r() * 100, r() * 100];
    const bruto = todos.reduce((m, p) => (Math.hypot(p.x - x, p.y - y) < Math.hypot(m.x - x, m.y - y) ? p : m));
    assert.equal(q.maisProximo(x, y), bruto);
  }
});

test('árvore vazia: nenhum resultado', () => {
  const q = new QuadTree(caixa);
  assert.equal(q.maisProximo(1, 1), null);
  assert.deepEqual(q.buscaRetangulo(caixa), []);
});

test('pontos duplicados não causam recursão infinita (profundidade máxima)', () => {
  const q = new QuadTree(caixa, { capacidade: 1, profundidadeMax: 5 });
  for (let i = 0; i < 10; i++) q.insere({ x: 25, y: 25, dados: i });
  assert.equal(q.tamanho, 10);
  assert.equal(q.buscaRaio(25, 25, 0).length, 10);
});

test('ponto na linha divisória pertence a exatamente um filho', () => {
  const q = new QuadTree(caixa, { capacidade: 1 });
  q.insere({ x: 1, y: 1 });
  q.insere({ x: 50, y: 50 });
  q.insere({ x: 50, y: 10 });
  assert.equal(q.tamanho, 3);
  assert.equal(q.buscaRetangulo(caixa).length, 3);
});
