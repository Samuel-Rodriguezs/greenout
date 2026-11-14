import test from 'node:test';
import assert from 'node:assert/strict';
import { criarJogo, criarDeTexto, jogadasValidas, jogar, vencedor, contarPecas } from './damas.js';

const VAZIO = '........';

test('posição inicial: 12 peças cada e 7 jogadas para as brancas', () => {
  const e = criarJogo();
  assert.deepEqual(contarPecas(e), { b: 12, p: 12 });
  assert.equal(jogadasValidas(e).length, 7);
});

test('movimento simples alterna a vez e não muta o original', () => {
  const e = criarJogo();
  const f = jogar(e, [5, 0], [4, 1]);
  assert.equal(f.vez, 'p');
  assert.equal(f.tabuleiro[4][1], 'b');
  assert.equal(e.tabuleiro[5][0], 'b');
});

test('jogada inválida lança erro', () => {
  assert.throws(() => jogar(criarJogo(), [5, 0], [3, 2]));
  assert.throws(() => jogar(criarJogo(), [5, 0], [5, 1]));
});

test('captura é obrigatória e remove a peça', () => {
  const e = criarDeTexto([VAZIO, VAZIO, VAZIO, '....p...', '...b....', VAZIO, VAZIO, 'b.......'].map((s, i) => s), 'b');
  // peça branca em (4,3) captura preta em (3,4) indo para (2,5)
  const js = jogadasValidas(e);
  assert.equal(js.length, 1);
  assert.deepEqual(js[0].captura, [3, 4]);
  const f = jogar(e, [4, 3], [2, 5]);
  assert.equal(f.tabuleiro[3][4], null);
  assert.deepEqual(contarPecas(f), { b: 2, p: 0 });
});

test('captura bloqueada por peça atrás', () => {
  const e = criarDeTexto([VAZIO, VAZIO, '.....p..', '....p...', '...b....', VAZIO, VAZIO, VAZIO], 'b');
  assert.ok(jogadasValidas(e).every((j) => j.captura === null));
});

test('promoção a dama e dama anda para trás', () => {
  let e = criarDeTexto([VAZIO, '.b......', '.....p..', VAZIO, VAZIO, VAZIO, VAZIO, VAZIO], 'b');
  e = jogar(e, [1, 1], [0, 0]);
  assert.equal(e.tabuleiro[0][0], 'B');
  e = jogar(e, [2, 5], [3, 4]);
  const js = jogadasValidas(e);
  assert.ok(js.some((j) => j.para[0] === 1 && j.para[1] === 1)); // dama desce
});

test('peça comum não anda para trás', () => {
  const e = criarDeTexto([VAZIO, VAZIO, VAZIO, VAZIO, '....b...', VAZIO, VAZIO, VAZIO], 'b');
  assert.ok(jogadasValidas(e).every((j) => j.para[0] === 3));
});

test('vencedor quando adversário fica sem jogadas', () => {
  const e = criarDeTexto([VAZIO, VAZIO, VAZIO, VAZIO, VAZIO, VAZIO, VAZIO, VAZIO].map((s, i) => (i === 4 ? '.b......' : s)), 'p');
  assert.equal(vencedor(e), 'b');
  assert.equal(vencedor(criarJogo()), null);
});

test('tabuleiro de texto precisa ser 8x8', () => {
  assert.throws(() => criarDeTexto(['....']));
});
