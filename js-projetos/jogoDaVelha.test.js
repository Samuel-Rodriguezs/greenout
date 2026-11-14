import test from 'node:test';
import assert from 'node:assert/strict';
import { novoTabuleiro, jogar, vencedor, terminou, melhorJogada, jogadasLivres } from './jogoDaVelha.js';

const montar = (s) => [...s].map((c) => (c === '.' ? null : c));

test('detecta vencedor e empate', () => {
  assert.equal(vencedor(montar('XXX......')), 'X');
  assert.equal(vencedor(montar('O...O...O')), 'O');
  assert.equal(terminou(montar('XOXXOOOXX')), true);
  assert.equal(vencedor(montar('XOXXOOOXX')), null);
});

test('jogar não muta e valida entradas', () => {
  const t = novoTabuleiro();
  const t2 = jogar(t, 4, 'X');
  assert.equal(t[4], null);
  assert.equal(t2[4], 'X');
  assert.throws(() => jogar(t2, 4, 'O'), /ocupada/);
  assert.throws(() => jogar(t, 9, 'X'), RangeError);
  assert.throws(() => jogar(t, 0, 'Z'), /inválido/);
  assert.throws(() => jogar(montar('XXX......'), 5, 'O'), /encerrado/);
});

test('IA completa a vitória quando possível', () => {
  assert.equal(melhorJogada(montar('XX.OO....'), 'X'), 2);
});

test('IA bloqueia a derrota', () => {
  assert.equal(melhorJogada(montar('XX..O....'), 'O'), 2);
});

test('IA contra IA sempre empata', () => {
  let t = novoTabuleiro();
  let vez = 'X';
  while (!terminou(t)) {
    t = jogar(t, melhorJogada(t, vez), vez);
    vez = vez === 'X' ? 'O' : 'X';
  }
  assert.equal(vencedor(t), null);
  assert.equal(jogadasLivres(t).length, 0);
});

test('IA nunca perde para qualquer resposta do adversário', () => {
  function explorar(t, vez) {
    if (terminou(t)) return assert.notEqual(vencedor(t), 'O');
    if (vez === 'X') return explorar(jogar(t, melhorJogada(t, 'X'), 'X'), 'O');
    for (const p of jogadasLivres(t)) explorar(jogar(t, p, 'O'), 'X');
  }
  explorar(novoTabuleiro(), 'X');
});
