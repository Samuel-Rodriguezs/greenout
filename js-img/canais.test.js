import test from 'node:test';
import assert from 'node:assert/strict';
import { dePixels, obter, criar } from './imagem.js';
import { extrairCanal, isolarCanal, trocarCanais, definirCanal, misturar, alphaBlend } from './canais.js';

const img = dePixels(3, 1, [[10, 20, 30, 40], [50, 60, 70, 80], [90, 100, 110, 120]]);

test('extrairCanal devolve cinza do canal', () => {
  assert.deepEqual(obter(extrairCanal(img, 'g'), 1, 0), [60, 60, 60, 255]);
  assert.deepEqual(obter(extrairCanal(img, 3), 2, 0), [120, 120, 120, 255]);
  assert.throws(() => extrairCanal(img, 'x'));
});

test('isolarCanal zera os outros', () => {
  assert.deepEqual(obter(isolarCanal(img, 'b'), 0, 0), [0, 0, 30, 40]);
  assert.throws(() => isolarCanal(img, 'a'));
});

test('trocarCanais bgr e validação', () => {
  assert.deepEqual(obter(trocarCanais(img, 'bgr'), 0, 0), [30, 20, 10, 40]);
  assert.deepEqual(obter(trocarCanais(img, 'rrr'), 1, 0), [50, 50, 50, 80]);
  assert.throws(() => trocarCanais(img, 'rg'));
});

test('definirCanal usa o cinza da fonte', () => {
  const fonte = dePixels(3, 1, [[1, 1, 1], [2, 2, 2], [3, 3, 3]]);
  assert.deepEqual(obter(definirCanal(img, 'r', fonte), 2, 0), [3, 100, 110, 120]);
  assert.throws(() => definirCanal(img, 'r', criar(2, 1)), RangeError);
});

test('misturar linear', () => {
  const a = criar(1, 1, [0, 100, 200, 255]);
  const b = criar(1, 1, [100, 200, 0, 255]);
  assert.deepEqual(obter(misturar(a, b, 0.25), 0, 0), [25, 125, 150, 255]);
  assert.deepEqual(obter(misturar(a, b, 0), 0, 0), [0, 100, 200, 255]);
});

test('alphaBlend com fundo opaco', () => {
  const fundo = criar(1, 1, [200, 100, 0, 255]);
  const frente = criar(1, 1, [0, 100, 200, 128]);
  // af = 128/255 = 0.50196 ; r = 200*(1-af)=99.6 -> 100 ; g = 100 ; b = 200*af = 100.39 -> 100
  assert.deepEqual(obter(alphaBlend(fundo, frente), 0, 0), [100, 100, 100, 255]);
  // opacidade 0 mantém o fundo
  assert.deepEqual(obter(alphaBlend(fundo, frente, 0), 0, 0), [200, 100, 0, 255]);
  // frente opaca cobre
  assert.deepEqual(obter(alphaBlend(fundo, criar(1, 1, [1, 2, 3, 255])), 0, 0), [1, 2, 3, 255]);
});

test('alphaBlend com fundo transparente herda a cor da frente', () => {
  const fundo = criar(1, 1, [0, 0, 0, 0]);
  const frente = criar(1, 1, [80, 90, 100, 128]);
  const p = obter(alphaBlend(fundo, frente), 0, 0);
  assert.deepEqual(p.slice(0, 3), [80, 90, 100]);
  assert.equal(p[3], 128);
});
