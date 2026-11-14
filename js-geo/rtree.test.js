import test from 'node:test';
import assert from 'node:assert/strict';
import { RTree } from './rtree.js';
import { criaBBox, intersecta } from './bbox.js';

function lcg(semente) {
  let s = semente;
  return () => (s = (s * 1664525 + 1013904223) % 4294967296) / 4294967296;
}

test('árvore vazia não encontra nada', () => {
  const t = new RTree();
  assert.deepEqual(t.busca(criaBBox(0, 0, 100, 100)), []);
  assert.equal(t.tamanho, 0);
  assert.equal(t.altura, 1);
});

test('insere poucos itens e busca por retângulo', () => {
  const t = new RTree();
  t.insere(criaBBox(0, 0, 2, 2), 'a');
  t.insere(criaBBox(5, 5, 7, 7), 'b');
  t.insere(criaBBox(1, 1, 6, 6), 'c');
  assert.deepEqual(t.busca(criaBBox(0, 0, 1, 1)).sort(), ['a', 'c']);
  assert.deepEqual(t.busca(criaBBox(6.5, 6.5, 9, 9)).sort(), ['b']);
  assert.deepEqual(t.busca(criaBBox(8, 8, 9, 9)), []);
});

test('muitos retângulos: resultado igual à varredura linear e árvore cresce', () => {
  const r = lcg(11);
  const itens = Array.from({ length: 600 }, (_, i) => {
    const x = r() * 1000, y = r() * 1000;
    return { caixa: criaBBox(x, y, x + r() * 20, y + r() * 20), id: i };
  });
  const t = new RTree(5);
  itens.forEach((it) => t.insere(it.caixa, it.id));
  assert.equal(t.tamanho, 600);
  assert.ok(t.altura >= 3);
  for (let q = 0; q < 30; q++) {
    const x = r() * 900, y = r() * 900;
    const area = criaBBox(x, y, x + r() * 150, y + r() * 150);
    const esperado = itens.filter((it) => intersecta(it.caixa, area)).map((it) => it.id).sort((a, b) => a - b);
    const achado = t.busca(area).sort((a, b) => a - b);
    assert.deepEqual(achado, esperado);
  }
});

test('pontos (caixas degeneradas) e toque de borda', () => {
  const t = new RTree();
  for (let i = 0; i < 50; i++) t.insereXY(i, i, i);
  assert.deepEqual(t.busca(criaBBox(10, 10, 12, 12)).sort((a, b) => a - b), [10, 11, 12]);
  assert.deepEqual(t.busca(criaBBox(49, 0, 60, 49)), [49]);
});

test('itens idênticos não quebram a divisão', () => {
  const t = new RTree(3);
  for (let i = 0; i < 20; i++) t.insereXY(5, 5, i);
  assert.equal(t.busca(criaBBox(5, 5, 5, 5)).length, 20);
});

test('capacidade inválida lança erro', () => {
  assert.throws(() => new RTree(2), RangeError);
});
