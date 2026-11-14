import test from 'node:test';
import assert from 'node:assert/strict';
import { diff, formatarDiff, aplicarDiff, estatisticas, lcs, similaridade } from './diffTextos.js';

test('textos iguais não geram mudanças', () => {
  const ops = diff('a\nb', 'a\nb');
  assert.deepEqual(estatisticas(ops), { adicionadas: 0, removidas: 0, iguais: 2 });
  assert.equal(similaridade('a\nb', 'a\nb'), 1);
});

test('adição, remoção e substituição', () => {
  assert.equal(formatarDiff(diff('a\nc', 'a\nb\nc')), '  a\n+ b\n  c');
  assert.equal(formatarDiff(diff('a\nb\nc', 'a\nc')), '  a\n- b\n  c');
  assert.equal(formatarDiff(diff('a\nb\nc', 'a\nX\nc')), '  a\n- b\n+ X\n  c');
});

test('entradas vazias', () => {
  assert.deepEqual(diff('', ''), []);
  assert.deepEqual(diff('', 'x'), [{ tipo: 'adicionado', linha: 'x' }]);
  assert.deepEqual(diff('x', ''), [{ tipo: 'removido', linha: 'x' }]);
  assert.equal(similaridade('', ''), 1);
});

test('tamanho da LCS', () => {
  const t = lcs(['A', 'B', 'C', 'B', 'D', 'A', 'B'], ['B', 'D', 'C', 'A', 'B', 'A']);
  assert.equal(t[0][0], 4);
});

test('aplicar o diff reconstrói ambos os textos', () => {
  const antes = 'um\ndois\ntres\nquatro\ncinco';
  const depois = 'um\ntres\nquatro\nseis\ncinco\nsete';
  const ops = diff(antes, depois);
  assert.equal(aplicarDiff(ops, 'depois'), depois);
  assert.equal(aplicarDiff(ops, 'antes'), antes);
});

test('diff mínimo: iguais = tamanho da LCS', () => {
  const antes = 'a\nb\nc\nd\ne';
  const depois = 'b\nc\nx\ne\nf';
  const ops = diff(antes, depois);
  assert.equal(estatisticas(ops).iguais, lcs(antes.split('\n'), depois.split('\n'))[0][0]);
});

test('similaridade parcial', () => {
  assert.equal(similaridade('a\nb', 'a\nc'), 0.5);
  assert.equal(similaridade('a', 'b'), 0);
});
