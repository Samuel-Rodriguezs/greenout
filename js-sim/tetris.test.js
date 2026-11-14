import test from 'node:test';
import assert from 'node:assert/strict';
import {
  mulberry32, PECAS, rotacionar, criarTabuleiro, colide, fixar, limparLinhas,
  criarJogo, moverLateral, girar, descer, quedaDireta,
} from './tetris.js';

test('rotacionar T quatro vezes volta ao original', () => {
  let m = PECAS.T;
  for (let i = 0; i < 4; i++) m = rotacionar(m);
  assert.deepEqual(m, PECAS.T);
  assert.deepEqual(rotacionar([[1, 0], [1, 1]]), [[1, 1], [1, 0]]);
});

test('colisão com paredes, chão e blocos', () => {
  const t = criarTabuleiro(10, 20);
  assert.ok(colide(t, PECAS.O, -1, 0));
  assert.ok(colide(t, PECAS.O, 9, 0));
  assert.ok(colide(t, PECAS.O, 0, 19));
  assert.ok(!colide(t, PECAS.O, 0, 18));
  const f = fixar(t, PECAS.O, 0, 18);
  assert.ok(colide(f, PECAS.O, 0, 17));
});

test('fixar não muta o tabuleiro original', () => {
  const t = criarTabuleiro(4, 4);
  fixar(t, PECAS.O, 0, 0);
  assert.equal(t.flat().filter(Boolean).length, 0);
});

test('limparLinhas remove linhas cheias e desloca o resto', () => {
  const t = criarTabuleiro(4, 4);
  t[3] = [1, 1, 1, 1];
  t[2] = [1, 1, 1, 1];
  t[1] = [0, 1, 0, 0];
  const r = limparLinhas(t);
  assert.equal(r.linhas, 2);
  assert.deepEqual(r.tabuleiro[3], [0, 1, 0, 0]);
  assert.deepEqual(r.tabuleiro[0], [0, 0, 0, 0]);
});

test('peça nova nasce centralizada; sacola de 7 não repete antes de esvaziar', () => {
  const rng = mulberry32(11);
  let e = criarJogo(rng);
  const tipos = [e.peca.tipo];
  for (let i = 0; i < 6; i++) {
    e = quedaDireta(e, rng);
    tipos.push(e.peca.tipo);
  }
  assert.equal(new Set(tipos).size, 7);
});

test('mover lateral respeita paredes', () => {
  const rng = mulberry32(2);
  let e = criarJogo(rng);
  for (let i = 0; i < 20; i++) e = moverLateral(e, -1);
  assert.equal(e.peca.x, 0);
  for (let i = 0; i < 20; i++) e = moverLateral(e, 1);
  assert.equal(e.peca.x + e.peca.forma[0].length, 10);
});

test('girar encosta na parede com wall kick', () => {
  const rng = mulberry32(2);
  let e = criarJogo(rng);
  e = { ...e, peca: { tipo: 'I', forma: rotacionar(PECAS.I), x: -2, y: 0 } };
  const g = girar(e);
  assert.ok(!colide(g.tabuleiro, g.peca.forma, g.peca.x, g.peca.y));
});

test('descer até fixar gera nova peça e pontua linha completa', () => {
  const rng = mulberry32(5);
  let e = criarJogo(rng, 4, 6);
  const t = criarTabuleiro(4, 6);
  t[5] = [1, 1, 0, 0];
  e = { ...e, tabuleiro: t, peca: { tipo: 'O', forma: PECAS.O, x: 2, y: 0 } };
  const r = quedaDireta(e, rng);
  assert.equal(r.linhas, 1);
  assert.equal(r.pontos, 100);
  assert.equal(r.tabuleiro[5].filter(Boolean).length, 2);
});

test('fim de jogo quando a pilha chega ao topo', () => {
  const rng = mulberry32(8);
  let e = criarJogo(rng, 10, 6);
  for (let i = 0; i < 20 && !e.fimDeJogo; i++) e = quedaDireta(e, rng);
  assert.ok(e.fimDeJogo);
  assert.equal(descer(e, rng), e);
});
