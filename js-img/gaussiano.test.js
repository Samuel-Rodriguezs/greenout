import test from 'node:test';
import assert from 'node:assert/strict';
import { deCinza, criar, obter, igual } from './imagem.js';
import { kernelGaussiano, blurGaussiano, blurPlano } from './gaussiano.js';
import { convolverPlano } from './convolucao.js';

const vals = (img) => Array.from({ length: img.largura * img.altura }, (_, i) => img.dados[i * 4]);

test('kernel normalizado, simétrico e com pico central', () => {
  const k = kernelGaussiano(1);
  assert.equal(k.length, 7);
  assert.ok(Math.abs(k.reduce((a, b) => a + b) - 1) < 1e-12);
  for (let i = 0; i < 3; i++) assert.ok(Math.abs(k[i] - k[6 - i]) < 1e-15);
  assert.ok(k[3] > k[2] && k[2] > k[1] && k[1] > k[0]);
  // razão k[±1]/k[0] = exp(-1/2)
  assert.ok(Math.abs(k[4] / k[3] - Math.exp(-0.5)) < 1e-12);
  assert.throws(() => kernelGaussiano(0), RangeError);
});

test('imagem constante não muda', () => {
  const img = criar(5, 5, [123, 45, 200, 255]);
  assert.ok(igual(blurGaussiano(img, 1.5), img));
});

test('impulso central vira o produto externo dos kernels 1D', () => {
  const dados = new Array(25).fill(0);
  dados[12] = 255;
  const r = blurGaussiano(deCinza(5, 5, dados), 1, 'zero');
  const k = kernelGaussiano(1);
  // raio 3 > metade da imagem; com borda zero, o centro recebe k0^2 * 255
  const esperado = (x, y) => Math.round(255 * k[3 + x - 2] * k[3 + y - 2]);
  for (let y = 0; y < 5; y++) for (let x = 0; x < 5; x++) assert.equal(obter(r, x, y)[0], esperado(x, y));
  assert.ok(obter(r, 2, 2)[0] > obter(r, 3, 2)[0]);
});

test('separável equivale à convolução 2D com o produto externo', () => {
  const p = Float64Array.from({ length: 36 }, (_, i) => (i * 37) % 101);
  const k = kernelGaussiano(0.8);
  const k2 = k.map((a) => k.map((b) => a * b));
  const a = blurPlano(p, 6, 6, 0.8, 'espelho');
  const b = convolverPlano(p, 6, 6, k2, 'espelho');
  for (let i = 0; i < 36; i++) assert.ok(Math.abs(a[i] - b[i]) < 1e-9);
});

test('blur suaviza degrau e conserva a média em borda clamp simétrica', () => {
  const img = deCinza(6, 1, [0, 0, 0, 200, 200, 200]);
  const r = vals(blurGaussiano(img, 1));
  assert.ok(r[2] > 0 && r[3] < 200);
  assert.equal(r[2] + r[3], 200); // simetria do degrau
  assert.ok(r[0] <= r[1] && r[1] <= r[2] && r[2] <= r[3]);
});
