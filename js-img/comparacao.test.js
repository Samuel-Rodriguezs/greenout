import test from 'node:test';
import assert from 'node:assert/strict';
import { criar, deCinza, dePixels } from './imagem.js';
import { mse, psnr, ssim } from './comparacao.js';

const perto = (a, b, tol = 1e-9) => assert.ok(Math.abs(a - b) < tol, `${a} != ${b}`);

test('imagens idênticas: mse 0, psnr infinito, ssim 1', () => {
  const a = deCinza(3, 3, [1, 2, 3, 40, 50, 60, 7, 8, 250]);
  assert.equal(mse(a, a), 0);
  assert.equal(psnr(a, a), Infinity);
  perto(ssim(a, a), 1);
  perto(ssim(a, a, 2), 1);
});

test('MSE calculado à mão', () => {
  // um pixel de 2 difere 10 em R, G e B: 3*100 / 6 = 50
  const a = dePixels(2, 1, [[100, 100, 100], [0, 0, 0]]);
  const b = dePixels(2, 1, [[110, 110, 110], [0, 0, 0]]);
  assert.equal(mse(a, b), 50);
  perto(psnr(a, b), 10 * Math.log10(65025 / 50));
  assert.ok(Math.abs(psnr(a, b) - 31.1) < 0.1);
});

test('MSE e PSNR de preto contra branco', () => {
  const k = criar(2, 2, [0, 0, 0, 255]);
  const w = criar(2, 2, [255, 255, 255, 255]);
  assert.equal(mse(k, w), 65025);
  perto(psnr(k, w), 0);
});

test('PSNR diminui quando o erro aumenta', () => {
  const base = criar(4, 4, [100, 100, 100, 255]);
  assert.ok(psnr(base, criar(4, 4, [101, 101, 101, 255])) > psnr(base, criar(4, 4, [120, 120, 120, 255])));
});

test('SSIM de cinzas constantes (fórmula fechada)', () => {
  const a = criar(3, 3, [100, 100, 100, 255]);
  const b = criar(3, 3, [110, 110, 110, 255]);
  const c1 = (0.01 * 255) ** 2;
  const esperado = (2 * 100 * 110 + c1) / (100 * 100 + 110 * 110 + c1);
  perto(ssim(a, b), esperado, 1e-6);
  assert.ok(ssim(a, b) < 1 && ssim(a, b) > 0.99);
});

test('SSIM cai com ruído estrutural e é simétrico', () => {
  const a = deCinza(4, 4, [0, 255, 0, 255, 255, 0, 255, 0, 0, 255, 0, 255, 255, 0, 255, 0]);
  const inv = deCinza(4, 4, Array.from({ length: 16 }, (_, i) => 255 - a.dados[i * 4]));
  assert.ok(ssim(a, inv) < 0.01); // padrões invertidos: correlação -1
  perto(ssim(a, inv), ssim(inv, a));
  const leve = deCinza(4, 4, Array.from({ length: 16 }, (_, i) => a.dados[i * 4] - (i === 5 ? 20 : 0) + (i === 0 ? 20 : 0)));
  assert.ok(ssim(a, leve) > 0.9 && ssim(a, leve) < 1);
});

test('tamanhos diferentes lançam erro', () => {
  assert.throws(() => mse(criar(2, 2), criar(3, 2)), RangeError);
  assert.throws(() => ssim(criar(2, 2), criar(2, 3)), RangeError);
});
