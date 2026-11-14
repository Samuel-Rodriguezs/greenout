import test from 'node:test';
import assert from 'node:assert/strict';
import { FilaPrioridade } from './filaPrioridade.js';

test('fila vazia', () => {
  const f = new FilaPrioridade();
  assert.equal(f.vazia, true);
  assert.equal(f.remover(), undefined);
  assert.equal(f.espiar(), undefined);
});
test('remove em ordem crescente', () => {
  const f = new FilaPrioridade(undefined, [5, 1, 4, 1, 3]);
  assert.equal(f.tamanho, 5);
  assert.deepEqual([...f], [1, 1, 3, 4, 5]);
  assert.equal(f.tamanho, 0);
});
test('comparador customizado (max-heap)', () => {
  const f = new FilaPrioridade((a, b) => b - a, [2, 9, 4]);
  assert.equal(f.remover(), 9);
  assert.equal(f.espiar(), 4);
});
test('objetos com prioridade, intercalando inserções', () => {
  const f = new FilaPrioridade((a, b) => a.p - b.p);
  f.inserir({ p: 3, n: 'c' }).inserir({ p: 1, n: 'a' });
  assert.equal(f.remover().n, 'a');
  f.inserir({ p: 2, n: 'b' });
  assert.deepEqual([...f].map((o) => o.n), ['b', 'c']);
});
test('aleatório', () => {
  const a = Array.from({ length: 1000 }, () => Math.random());
  const f = new FilaPrioridade(undefined, a);
  assert.deepEqual([...f], [...a].sort((x, y) => x - y));
});
