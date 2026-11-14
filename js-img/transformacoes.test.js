import test from 'node:test';
import assert from 'node:assert/strict';
import { deCinza, igual } from './imagem.js';
import { espelharHorizontal, espelharVertical, transpor, rotacionar90, rotacionar } from './transformacoes.js';

const vals = (img) => Array.from({ length: img.largura * img.altura }, (_, i) => img.dados[i * 4]);
// 3x2:  1 2 3 / 4 5 6
const img = deCinza(3, 2, [1, 2, 3, 4, 5, 6]);

test('espelhamentos', () => {
  assert.deepEqual(vals(espelharHorizontal(img)), [3, 2, 1, 6, 5, 4]);
  assert.deepEqual(vals(espelharVertical(img)), [4, 5, 6, 1, 2, 3]);
  assert.ok(igual(espelharHorizontal(espelharHorizontal(img)), img));
});

test('transposição troca dimensões', () => {
  const t = transpor(img);
  assert.equal(t.largura, 2);
  assert.equal(t.altura, 3);
  assert.deepEqual(vals(t), [1, 4, 2, 5, 3, 6]);
});

test('rotação de 90 graus horária', () => {
  const r = rotacionar90(img, 1);
  assert.equal(r.largura, 2);
  assert.equal(r.altura, 3);
  // colunas da original de baixo para cima viram linhas: 4 1 / 5 2 / 6 3
  assert.deepEqual(vals(r), [4, 1, 5, 2, 6, 3]);
});

test('rotação 180, 270, -90 e 360', () => {
  assert.deepEqual(vals(rotacionar90(img, 2)), [6, 5, 4, 3, 2, 1]);
  assert.ok(igual(rotacionar90(img, 2), espelharVertical(espelharHorizontal(img))));
  assert.ok(igual(rotacionar90(img, 3), rotacionar90(img, -1)));
  assert.deepEqual(vals(rotacionar90(img, 3)), [3, 6, 2, 5, 1, 4]);
  const r4 = rotacionar90(img, 4);
  assert.ok(igual(r4, img));
  assert.notEqual(r4, img);
  assert.throws(() => rotacionar90(img, 0.5), RangeError);
});

test('rotação livre: 0 é identidade e 90 em quadrado ímpar coincide com a exata', () => {
  const q = deCinza(3, 3, [1, 2, 3, 4, 5, 6, 7, 8, 9]);
  assert.ok(igual(rotacionar(q, 0), q));
  assert.ok(igual(rotacionar(q, 90), rotacionar90(q, 1)));
  assert.ok(igual(rotacionar(q, 180), rotacionar90(q, 2)));
  assert.deepEqual(vals(rotacionar(q, 90)), [7, 4, 1, 8, 5, 2, 9, 6, 3]);
});

test('rotação de 45 graus deixa fundo nos cantos', () => {
  const q = deCinza(5, 5, new Array(25).fill(9));
  const r = rotacionar(q, 45, [0, 0, 0, 0]);
  assert.equal(r.dados[3], 0); // canto (0,0) sem origem -> alfa 0
  assert.equal(r.dados[12 * 4], 9); // centro preservado
});
