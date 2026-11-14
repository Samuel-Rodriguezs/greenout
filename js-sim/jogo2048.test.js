import test from 'node:test';
import assert from 'node:assert/strict';
import { mulberry32, criarGrade, adicionarPeca, novoJogo, deslizarLinha, mover, jogar, fimDeJogo, venceu } from './jogo2048.js';

test('deslizarLinha funde uma vez por peça', () => {
  assert.deepEqual(deslizarLinha([2, 2, 2, 2]), { linha: [4, 4, 0, 0], pontos: 8 });
  assert.deepEqual(deslizarLinha([2, 2, 4, 0]), { linha: [4, 4, 0, 0], pontos: 4 });
  assert.deepEqual(deslizarLinha([0, 2, 0, 2]), { linha: [4, 0, 0, 0], pontos: 4 });
  assert.deepEqual(deslizarLinha([2, 4, 8, 16]), { linha: [2, 4, 8, 16], pontos: 0 });
});

test('mover nas quatro direções', () => {
  const g = [
    [2, 0, 0, 2],
    [0, 0, 0, 0],
    [4, 0, 0, 0],
    [4, 0, 0, 0],
  ];
  assert.deepEqual(mover(g, 'esquerda').grade[0], [4, 0, 0, 0]);
  assert.deepEqual(mover(g, 'direita').grade[0], [0, 0, 0, 4]);
  const cima = mover(g, 'cima');
  assert.deepEqual(cima.grade.map((l) => l[0]), [2, 8, 0, 0]);
  assert.equal(cima.pontos, 8);
  const baixo = mover(g, 'baixo');
  assert.deepEqual(baixo.grade.map((l) => l[0]), [0, 0, 2, 8]);
});

test('mover sem alteração não "moveu"; direção inválida lança', () => {
  const g = [[2, 4], [8, 16]];
  assert.equal(mover(g, 'esquerda').moveu, false);
  assert.throws(() => mover(g, 'diagonal'));
});

test('adicionarPeca determinística e sem mutar', () => {
  const g = criarGrade(4);
  const a = adicionarPeca(g, mulberry32(5));
  const b = adicionarPeca(g, mulberry32(5));
  assert.deepEqual(a, b);
  assert.equal(g.flat().filter(Boolean).length, 0);
  assert.equal(a.flat().filter(Boolean).length, 1);
});

test('novoJogo tem duas peças; jogar adiciona peça só se moveu', () => {
  const rng = mulberry32(1);
  const e = novoJogo(rng);
  assert.equal(e.grade.flat().filter(Boolean).length, 2);
  let s = e;
  for (const d of ['esquerda', 'cima', 'direita', 'baixo']) s = jogar(s, d, rng);
  assert.ok(s.grade.flat().filter(Boolean).length >= 2);
  const travado = { grade: [[2, 4], [8, 16]], pontos: 0 };
  assert.equal(jogar(travado, 'esquerda', rng), travado);
});

test('fim de jogo e vitória', () => {
  assert.ok(fimDeJogo([[2, 4], [8, 16]]));
  assert.ok(!fimDeJogo([[2, 2], [8, 16]]));
  assert.ok(venceu([[2048, 0], [0, 0]]));
  assert.ok(!venceu([[1024, 0], [0, 0]]));
});

test('partida simulada termina com soma coerente', () => {
  const rng = mulberry32(99);
  let s = novoJogo(rng);
  const dirs = ['esquerda', 'cima', 'direita', 'baixo'];
  for (let i = 0; i < 2000 && !fimDeJogo(s.grade); i++) s = jogar(s, dirs[i % 4], rng);
  assert.ok(fimDeJogo(s.grade));
  assert.ok(s.pontos > 0);
});
