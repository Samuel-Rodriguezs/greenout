import test from 'node:test';
import assert from 'node:assert/strict';
import { permutacoes, combinacoes, subconjuntos, produtoCartesiano, proximaPermutacao, fatorial } from './combinatoria.js';

test('permutações de 3', () => {
  assert.deepEqual([...permutacoes([1, 2, 3])], [[1, 2, 3], [1, 3, 2], [2, 1, 3], [2, 3, 1], [3, 1, 2], [3, 2, 1]]);
});
test('permutações: vazio, k parcial e k inválido', () => {
  assert.deepEqual([...permutacoes([])], [[]]);
  assert.equal([...permutacoes([1, 2, 3, 4], 2)].length, 12);
  assert.deepEqual([...permutacoes([1, 2], 3)], []);
  assert.deepEqual([...permutacoes([1, 2], -1)], []);
});
test('permutações: quantidade e unicidade', () => {
  const ps = [...permutacoes('abcde'.split(''))];
  assert.equal(ps.length, fatorial(5));
  assert.equal(new Set(ps.map((p) => p.join(''))).size, 120);
});
test('combinações', () => {
  assert.deepEqual([...combinacoes(['a', 'b', 'c', 'd'], 2)], [['a', 'b'], ['a', 'c'], ['a', 'd'], ['b', 'c'], ['b', 'd'], ['c', 'd']]);
  assert.deepEqual([...combinacoes([1, 2], 0)], [[]]);
  assert.deepEqual([...combinacoes([1, 2], 2)], [[1, 2]]);
  assert.deepEqual([...combinacoes([1, 2], 3)], []);
  assert.equal([...combinacoes(Array.from({ length: 10 }, (_, i) => i), 4)].length, 210);
});
test('subconjuntos', () => {
  assert.deepEqual([...subconjuntos([])], [[]]);
  assert.deepEqual([...subconjuntos([1, 2])], [[], [1], [2], [1, 2]]);
  assert.equal([...subconjuntos([1, 2, 3, 4, 5])].length, 32);
  assert.throws(() => [...subconjuntos(new Array(31))], RangeError);
});
test('produto cartesiano', () => {
  assert.deepEqual([...produtoCartesiano([1, 2], ['a', 'b'])], [[1, 'a'], [1, 'b'], [2, 'a'], [2, 'b']]);
  assert.deepEqual([...produtoCartesiano([1], [2], [3])], [[1, 2, 3]]);
  assert.deepEqual([...produtoCartesiano([1, 2], [])], []);
  assert.deepEqual([...produtoCartesiano()], [[]]);
});
test('próxima permutação', () => {
  const v = [1, 2, 3];
  const vistos = [v.join('')];
  while (proximaPermutacao(v)) vistos.push(v.join(''));
  assert.deepEqual(vistos, ['123', '132', '213', '231', '312', '321']);
  assert.equal(proximaPermutacao([3, 2, 1]), false);
  const d = [1, 1, 2];
  assert.equal(proximaPermutacao(d), true);
  assert.deepEqual(d, [1, 2, 1]);
});
test('são preguiçosos', () => {
  const g = permutacoes(Array.from({ length: 20 }, (_, i) => i));
  assert.deepEqual(g.next().value.slice(0, 3), [0, 1, 2]);
});
