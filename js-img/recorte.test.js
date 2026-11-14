import test from 'node:test';
import assert from 'node:assert/strict';
import { deCinza, obter } from './imagem.js';
import { recortar, acolchoar, recorteCentral, aparar } from './recorte.js';

const vals = (img) => Array.from({ length: img.largura * img.altura }, (_, i) => img.dados[i * 4]);
const g = deCinza(4, 3, [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]);

test('recortar extrai o retângulo', () => {
  const r = recortar(g, 1, 1, 2, 2);
  assert.equal(r.largura, 2);
  assert.deepEqual(vals(r), [6, 7, 10, 11]);
  assert.deepEqual(vals(recortar(g, 0, 0, 4, 3)), vals(g));
});

test('recortar fora da imagem lança erro', () => {
  assert.throws(() => recortar(g, 3, 0, 2, 1), RangeError);
  assert.throws(() => recortar(g, -1, 0, 1, 1), RangeError);
  assert.throws(() => recortar(g, 0, 0, 0, 1), RangeError);
});

test('padding constante', () => {
  const p = acolchoar(deCinza(2, 1, [7, 8]), { topo: 1, esquerda: 1, direita: 1 }, 'constante', [9, 9, 9, 255]);
  assert.equal(p.largura, 4);
  assert.equal(p.altura, 2);
  assert.deepEqual(vals(p), [9, 9, 9, 9, 9, 7, 8, 9]);
});

test('padding clamp, wrap e espelho em linha [1,2,3]', () => {
  const l = deCinza(3, 1, [1, 2, 3]);
  const m = { esquerda: 2, direita: 2 };
  assert.deepEqual(vals(acolchoar(l, m, 'clamp')), [1, 1, 1, 2, 3, 3, 3]);
  assert.deepEqual(vals(acolchoar(l, m, 'wrap')), [2, 3, 1, 2, 3, 1, 2]);
  assert.deepEqual(vals(acolchoar(l, m, 'espelho')), [2, 1, 1, 2, 3, 3, 2]);
});

test('padding valida margens', () => {
  assert.throws(() => acolchoar(g, { topo: -1 }), RangeError);
});

test('recorte central', () => {
  assert.deepEqual(vals(recorteCentral(g, 2, 1)), [6, 7]);
});

test('aparar remove moldura da cor do canto', () => {
  const img = deCinza(5, 4, [0, 0, 0, 0, 0, 0, 0, 5, 6, 0, 0, 0, 7, 0, 0, 0, 0, 0, 0, 0]);
  const r = aparar(img);
  assert.equal(r.largura, 2);
  assert.equal(r.altura, 2);
  assert.deepEqual(vals(r), [5, 6, 7, 0]);
  assert.equal(aparar(deCinza(2, 2, [4, 4, 4, 4])), null);
  assert.equal(obter(r, 1, 0)[0], 6);
});
