import test from 'node:test';
import assert from 'node:assert/strict';
import { mulberry32, embaralhar, criarJogo, virar } from './jogoDaMemoria.js';

test('embaralhar preserva elementos e é determinístico', () => {
  const l = [1, 2, 3, 4, 5, 6];
  const a = embaralhar(l, mulberry32(9));
  assert.deepEqual(a.slice().sort(), l);
  assert.deepEqual(a, embaralhar(l, mulberry32(9)));
  assert.deepEqual(l, [1, 2, 3, 4, 5, 6]);
});

test('cada valor aparece duas vezes; valores repetidos lançam erro', () => {
  const j = criarJogo(['a', 'b', 'c'], mulberry32(1));
  assert.equal(j.cartas.length, 6);
  for (const v of 'abc') assert.equal(j.cartas.filter((c) => c.valor === v).length, 2);
  assert.throws(() => criarJogo(['a', 'a'], mulberry32(1)));
});

function posicoes(j, v) {
  return j.cartas.map((c, i) => (c.valor === v ? i : -1)).filter((i) => i >= 0);
}

test('par encontrado fica travado', () => {
  let j = criarJogo(['a', 'b'], mulberry32(3));
  const [x, y] = posicoes(j, 'a');
  j = virar(j, x);
  j = virar(j, y);
  assert.equal(j.cartas[x].estado, 'par');
  assert.equal(j.tentativas, 1);
  assert.deepEqual(j.viradas, []);
});

test('par errado é ocultado na jogada seguinte', () => {
  let j = criarJogo(['a', 'b'], mulberry32(3));
  const [a1] = posicoes(j, 'a');
  const [b1] = posicoes(j, 'b');
  j = virar(j, a1);
  j = virar(j, b1);
  assert.equal(j.cartas[a1].estado, 'virada');
  assert.equal(j.cartas[b1].estado, 'virada');
  j = virar(j, a1);
  assert.equal(j.cartas[b1].estado, 'oculta');
  assert.equal(j.cartas[a1].estado, 'virada');
});

test('virar carta já virada não conta tentativa', () => {
  let j = criarJogo(['a', 'b'], mulberry32(3));
  j = virar(j, 0);
  const k = virar(j, 0);
  assert.equal(k.tentativas, 0);
  assert.deepEqual(k.viradas, [0]);
});

test('vitória ao achar todos os pares', () => {
  let j = criarJogo(['a', 'b', 'c'], mulberry32(4));
  for (const v of 'abc') for (const i of posicoes(j, v)) j = virar(j, i);
  assert.equal(j.status, 'venceu');
  assert.equal(j.tentativas, 3);
  assert.equal(virar(j, 0), j);
  assert.throws(() => virar(criarJogo(['a'], mulberry32(1)), 5));
});
