import test from 'node:test';
import assert from 'node:assert/strict';
import { criarTabuleiro, jogar, vencedor, empate, colunasValidas, melhorJogada, avaliar } from './conecta4.js';

function sequencia(cols, primeiro = 1) {
  let t = criarTabuleiro();
  let j = primeiro;
  for (const c of cols) {
    t = jogar(t, c, j);
    j = j === 1 ? 2 : 1;
  }
  return t;
}

test('peça cai até o fundo e empilha', () => {
  let t = jogar(criarTabuleiro(), 2, 1);
  t = jogar(t, 2, 2);
  assert.equal(t[5][2], 1);
  assert.equal(t[4][2], 2);
});

test('coluna cheia ou inexistente lança erro', () => {
  let t = criarTabuleiro();
  for (let i = 0; i < 6; i++) t = jogar(t, 0, 1);
  assert.throws(() => jogar(t, 0, 2));
  assert.throws(() => jogar(t, 7, 1));
  assert.ok(!colunasValidas(t).includes(0));
});

test('vitórias horizontal, vertical e diagonais', () => {
  assert.equal(vencedor(sequencia([0, 0, 1, 1, 2, 2, 3])), 1);
  assert.equal(vencedor(sequencia([0, 1, 0, 1, 0, 1, 0])), 1);
  // diagonal ascendente para o jogador 1
  assert.equal(vencedor(sequencia([0, 1, 1, 2, 2, 3, 2, 3, 3, 6, 3])), 1);
  // diagonal descendente
  assert.equal(vencedor(sequencia([3, 2, 2, 1, 1, 0, 1, 0, 0, 6, 0])), 1);
  assert.equal(vencedor(criarTabuleiro()), 0);
});

test('IA completa vitória imediata', () => {
  const t = sequencia([0, 6, 1, 6, 2, 5]);
  assert.equal(melhorJogada(t, 1, 3), 3);
});

test('IA bloqueia vitória do adversário', () => {
  // jogador 2 ameaça colunas 0..2; jogador 1 deve jogar em 3
  let t = criarTabuleiro();
  t = jogar(t, 0, 2);
  t = jogar(t, 1, 2);
  t = jogar(t, 2, 2);
  t = jogar(t, 6, 1);
  t = jogar(t, 6, 1);
  assert.equal(melhorJogada(t, 1, 4), 3);
});

test('IA enxerga vitória em 2 jogadas (garfo)', () => {
  // 1 tem _ 1 1 _ na base com 0 e 4 liberados: jogar 2 ou 3 cria dupla ameaça
  let t = criarTabuleiro();
  t = jogar(t, 2, 1);
  t = jogar(t, 3, 1);
  t = jogar(t, 6, 2);
  t = jogar(t, 6, 2);
  const c = melhorJogada(t, 1, 4);
  assert.ok([1, 4].includes(c));
});

test('tabuleiro vazio: IA escolhe o centro', () => {
  assert.equal(melhorJogada(criarTabuleiro(), 1, 3), 3);
});

test('avaliar favorece o centro e é simétrico em sinal', () => {
  const t = jogar(criarTabuleiro(), 3, 1);
  assert.ok(avaliar(t, 1) > avaliar(t, 2) - 1);
  assert.ok(avaliar(t, 1) > 0);
});

test('empate em tabuleiro cheio sem vencedor', () => {
  const padrao = [
    [1, 1, 2, 2, 1, 1, 2],
    [2, 2, 1, 1, 2, 2, 1],
    [1, 1, 2, 2, 1, 1, 2],
    [2, 2, 1, 1, 2, 2, 1],
    [1, 1, 2, 2, 1, 1, 2],
    [2, 2, 1, 1, 2, 2, 1],
  ];
  assert.equal(vencedor(padrao), 0);
  assert.ok(empate(padrao));
  assert.equal(melhorJogada(padrao, 1), null);
});

test('IA vence partida contra jogador que sempre joga a primeira coluna livre', () => {
  let t = criarTabuleiro();
  let vez = 1;
  for (let i = 0; i < 42 && !vencedor(t) && !empate(t); i++) {
    const c = vez === 1 ? melhorJogada(t, 1, 4) : [0, 1, 2, 3, 4, 5, 6].find((k) => colunasValidas(t).includes(k));
    t = jogar(t, c, vez);
    vez = vez === 1 ? 2 : 1;
  }
  assert.equal(vencedor(t), 1);
});
