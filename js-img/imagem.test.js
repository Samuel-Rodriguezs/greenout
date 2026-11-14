import test from 'node:test';
import assert from 'node:assert/strict';
import { criar, dePixels, deCinza, obter, definir, obterBorda, indiceBorda, clonar, igual, dentro } from './imagem.js';

test('criar preenche com a cor e valida dimensões', () => {
  const img = criar(3, 2, [10, 20, 30, 255]);
  assert.equal(img.dados.length, 24);
  assert.deepEqual(obter(img, 2, 1), [10, 20, 30, 255]);
  assert.throws(() => criar(0, 2), RangeError);
  assert.throws(() => criar(2.5, 2), RangeError);
});

test('obter/definir respeitam os limites', () => {
  const img = criar(3, 3);
  definir(img, 1, 2, [1, 2, 3]);
  assert.deepEqual(obter(img, 1, 2), [1, 2, 3, 255]);
  assert.equal(dentro(img, 3, 0), false);
  assert.throws(() => obter(img, -1, 0), RangeError);
  assert.throws(() => definir(img, 0, 3, [0, 0, 0]), RangeError);
});

test('dePixels e deCinza montam na ordem de linhas', () => {
  const img = dePixels(2, 1, [[255, 0, 0], [0, 0, 255, 128]]);
  assert.deepEqual(Array.from(img.dados), [255, 0, 0, 255, 0, 0, 255, 128]);
  const g = deCinza(2, 1, [7, 9]);
  assert.deepEqual(obter(g, 1, 0), [9, 9, 9, 255]);
  assert.throws(() => deCinza(2, 2, [1]), RangeError);
});

test('indiceBorda: clamp, wrap, espelho e zero', () => {
  assert.equal(indiceBorda(-2, 4, 'clamp'), 0);
  assert.equal(indiceBorda(6, 4, 'clamp'), 3);
  assert.equal(indiceBorda(-1, 4, 'wrap'), 3);
  assert.equal(indiceBorda(5, 4, 'wrap'), 1);
  assert.equal(indiceBorda(-1, 4, 'espelho'), 0);
  assert.equal(indiceBorda(-2, 4, 'espelho'), 1);
  assert.equal(indiceBorda(4, 4, 'espelho'), 3);
  assert.equal(indiceBorda(5, 4, 'espelho'), 2);
  assert.equal(indiceBorda(9, 4, 'espelho'), 1); // 9 mod 8 = 1
  assert.equal(indiceBorda(4, 4, 'zero'), -1);
  assert.throws(() => indiceBorda(4, 4, 'x'));
});

test('obterBorda lê pixels virtuais', () => {
  const img = dePixels(2, 2, [[1, 0, 0], [2, 0, 0], [3, 0, 0], [4, 0, 0]]);
  assert.equal(obterBorda(img, -1, -1, 'clamp')[0], 1);
  assert.equal(obterBorda(img, 2, 0, 'wrap')[0], 1);
  assert.equal(obterBorda(img, 2, 1, 'espelho')[0], 4);
  assert.deepEqual(obterBorda(img, 5, 5, 'zero'), [0, 0, 0, 0]);
});

test('clonar é cópia independente e igual compara', () => {
  const a = criar(2, 2, [5, 5, 5, 255]);
  const b = clonar(a);
  assert.ok(igual(a, b));
  definir(b, 0, 0, [9, 9, 9]);
  assert.ok(!igual(a, b));
  assert.deepEqual(obter(a, 0, 0), [5, 5, 5, 255]);
  assert.ok(!igual(a, criar(3, 2)));
});
