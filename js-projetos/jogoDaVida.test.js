import test from 'node:test';
import assert from 'node:assert/strict';
import { criarGrade, contarVizinhas, proximaGeracao, simular, paraTexto, deTexto, populacao } from './jogoDaVida.js';

test('bloco é uma vida estável', () => {
  const g = criarGrade(4, 4, [[1, 1], [1, 2], [2, 1], [2, 2]]);
  assert.deepEqual(proximaGeracao(g), g);
});

test('blinker oscila com período 2', () => {
  const h = deTexto('.....\n.....\n.###.\n.....\n.....');
  const v = proximaGeracao(h);
  assert.equal(paraTexto(v), '.....\n..#..\n..#..\n..#..\n.....');
  assert.deepEqual(simular(h, 2), h);
});

test('planador se desloca após 4 gerações', () => {
  const g = deTexto('.#....\n..#...\n###...\n......\n......\n......');
  const r = simular(g, 4);
  assert.equal(paraTexto(r), '......\n..#...\n...#..\n.###..\n......\n......');
});

test('contarVizinhas respeita bordas', () => {
  const g = criarGrade(3, 3, [[0, 1], [1, 0]]);
  assert.equal(contarVizinhas(g, 0, 0), 2);
  assert.equal(contarVizinhas(g, 2, 2), 0);
});

test('população e ida/volta de texto', () => {
  const g = deTexto('#.#\n.#.');
  assert.equal(populacao(g), 3);
  assert.equal(paraTexto(g), '#.#\n.#.');
});

test('erros de entrada', () => {
  assert.throws(() => criarGrade(0, 3), RangeError);
  assert.throws(() => criarGrade(2, 2, [[5, 5]]), /fora da grade/);
});
