import test from 'node:test';
import assert from 'node:assert/strict';
import { mulberry32, normalizar, escolherPalavra, criarJogo, chutar, mascara } from './forca.js';

test('normalizar remove acentos', () => {
  assert.equal(normalizar('Coração'), 'coracao');
});

test('mulberry32 é determinístico', () => {
  const a = mulberry32(42);
  const b = mulberry32(42);
  assert.deepEqual([a(), a(), a()], [b(), b(), b()]);
});

test('escolherPalavra usa o rng', () => {
  const lista = ['a', 'b', 'c'];
  assert.equal(escolherPalavra(lista, () => 0), 'a');
  assert.equal(escolherPalavra(lista, () => 0.99), 'c');
  assert.throws(() => escolherPalavra([], () => 0));
});

test('acertos e máscara com acentos', () => {
  let j = criarJogo('coração');
  j = chutar(j, 'c');
  j = chutar(j, 'A');
  assert.equal(mascara(j), 'c _ _ a ç ã _');
  j = chutar(j, 'o');
  assert.equal(mascara(j), 'c o _ a ç ã o');
});

test('vitória', () => {
  let j = criarJogo('gato');
  for (const l of 'gato') j = chutar(j, l);
  assert.equal(j.status, 'venceu');
});

test('derrota após maxErros e jogo congela', () => {
  let j = criarJogo('gato', 3);
  for (const l of 'xyz') j = chutar(j, l);
  assert.equal(j.status, 'perdeu');
  assert.equal(chutar(j, 'g'), j);
});

test('chute repetido não penaliza e chute inválido lança', () => {
  let j = criarJogo('gato');
  j = chutar(j, 'x');
  const k = chutar(j, 'x');
  assert.equal(k.erros.length, 1);
  assert.throws(() => chutar(j, '1'));
  assert.throws(() => chutar(j, 'ab'));
});

test('hífen é revelado desde o início', () => {
  const j = criarJogo('guarda-chuva');
  assert.match(mascara(j), /_ - _/);
});
