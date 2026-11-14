import test from 'node:test';
import assert from 'node:assert/strict';
import { obter, igual } from './imagem.js';
import { gradienteHorizontal, gradienteVertical, gradienteRadial, xadrez, listras, ruido, prng } from './gerador.js';

const linhaR = (img, y = 0) => Array.from({ length: img.largura }, (_, x) => obter(img, x, y)[0]);

test('gradiente horizontal 5x1 preto -> branco', () => {
  // 0, 63.75, 127.5, 191.25, 255
  assert.deepEqual(linhaR(gradienteHorizontal(5, 1, [0, 0, 0], [255, 255, 255])), [0, 64, 128, 191, 255]);
});

test('gradiente horizontal é constante nas colunas e interpola canais', () => {
  const g = gradienteHorizontal(3, 2, [0, 100, 200], [100, 0, 0]);
  assert.deepEqual(obter(g, 1, 1), [50, 50, 100, 255]);
  assert.deepEqual(obter(g, 1, 0), obter(g, 1, 1));
  assert.deepEqual(obter(gradienteHorizontal(1, 1, [9, 9, 9], [1, 1, 1]), 0, 0), [9, 9, 9, 255]);
});

test('gradiente vertical e radial', () => {
  const v = gradienteVertical(2, 3, [0, 0, 0], [200, 200, 200]);
  assert.deepEqual([obter(v, 0, 0)[0], obter(v, 1, 1)[0], obter(v, 0, 2)[0]], [0, 100, 200]);
  const r = gradienteRadial(3, 3, [255, 255, 255], [0, 0, 0]);
  assert.equal(obter(r, 1, 1)[0], 255);
  assert.equal(obter(r, 0, 0)[0], 0);
  // borda do meio: distância 1 / sqrt(2) = 0.7071 -> 255*(1-0.7071) = 74.7
  assert.equal(obter(r, 1, 0)[0], 75);
});

test('xadrez com casas de 2 pixels em 4x4', () => {
  const x = xadrez(4, 4, 2);
  const l0 = linhaR(x, 0);
  const l2 = linhaR(x, 2);
  assert.deepEqual(l0, [255, 255, 0, 0]);
  assert.deepEqual(linhaR(x, 1), l0);
  assert.deepEqual(l2, [0, 0, 255, 255]);
  assert.throws(() => xadrez(4, 4, 0), RangeError);
});

test('listras verticais', () => {
  assert.deepEqual(linhaR(listras(6, 2, 2, [200, 0, 0], [0, 0, 0])), [200, 200, 0, 0, 200, 200]);
});

test('ruído é determinístico por semente e cobre a faixa', () => {
  const a = ruido(8, 8, 42);
  assert.ok(igual(a, ruido(8, 8, 42)));
  assert.ok(!igual(a, ruido(8, 8, 43)));
  const grande = ruido(64, 64, 7);
  const vals = Array.from({ length: 4096 }, (_, i) => grande.dados[i * 4]);
  const media = vals.reduce((s, v) => s + v, 0) / vals.length;
  assert.ok(media > 120 && media < 135, `média ${media}`);
  assert.ok(Math.min(...vals) < 8 && Math.max(...vals) > 247);
  const c = ruido(2, 2, 1, false);
  assert.ok(obter(c, 0, 0)[0] !== obter(c, 0, 0)[1] || obter(c, 1, 1)[1] !== obter(c, 1, 1)[2]);
});

test('prng reprodutível em [0,1)', () => {
  const p = prng(123);
  const q = prng(123);
  for (let i = 0; i < 100; i++) {
    const v = p();
    assert.equal(v, q());
    assert.ok(v >= 0 && v < 1);
  }
});
