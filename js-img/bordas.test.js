import test from 'node:test';
import assert from 'node:assert/strict';
import { deCinza, obter, criar } from './imagem.js';
import { sobel, sobelPlanos, canny } from './bordas.js';

const vals = (img) => Array.from({ length: img.largura * img.altura }, (_, i) => img.dados[i * 4]);

test('sobelPlanos em degrau vertical 3x3', () => {
  const p = Float64Array.from([0, 0, 100, 0, 0, 100, 0, 0, 100]);
  const { gx, gy, mag } = sobelPlanos(p, 3, 3);
  // centro: (1+2+1)*100 - 0 = 400 ; gy = 0
  assert.equal(gx[4], 400);
  assert.equal(gy[4], 0);
  assert.equal(mag[4], 400);
  // coluna esquerda com clamp: vizinho esquerdo = ela mesma (0), direito = 0 -> 0
  assert.equal(gx[3], 0);
  // coluna direita: 100 - 0 ... (direita clamp=100, esquerda=0) -> 400
  assert.equal(gx[5], 400);
});

test('sobelPlanos detecta degrau horizontal (gy)', () => {
  const p = Float64Array.from([0, 0, 0, 0, 0, 0, 50, 50, 50]);
  const { gx, gy } = sobelPlanos(p, 3, 3);
  assert.equal(gx[4], 0);
  assert.equal(gy[4], 200); // 4*50
});

test('sobel: imagem plana sem bordas; degrau satura', () => {
  assert.ok(vals(sobel(criar(4, 4, [80, 80, 80, 255]))).every((v) => v === 0));
  const s = sobel(deCinza(3, 3, [0, 0, 255, 0, 0, 255, 0, 0, 255]));
  assert.deepEqual(vals(s), [0, 255, 255, 0, 255, 255, 0, 255, 255]);
});

test('sobel em rampa diagonal tem magnitude uniforme no interior', () => {
  const g = deCinza(4, 4, Array.from({ length: 16 }, (_, i) => ((i % 4) + Math.floor(i / 4)) * 10));
  const { mag } = sobelPlanos(Float64Array.from(vals(g)), 4, 4);
  // gx = gy = 8*10 = 80 -> |g| = 80*sqrt(2)
  assert.ok(Math.abs(mag[5] - 80 * Math.SQRT2) < 1e-9);
  assert.ok(Math.abs(mag[10] - 80 * Math.SQRT2) < 1e-9);
});

test('canny: degrau vertical vira uma linha fina de 1 pixel', () => {
  const dados = [];
  for (let y = 0; y < 8; y++) for (let x = 0; x < 8; x++) dados.push(x < 4 ? 0 : 255);
  const e = canny(deCinza(8, 8, dados), { sigma: 1, baixo: 30, alto: 100 });
  for (let y = 0; y < 8; y++) {
    const linha = [];
    for (let x = 0; x < 8; x++) linha.push(obter(e, x, y)[0]);
    assert.deepEqual(linha, [0, 0, 0, 0, 255, 0, 0, 0]);
  }
});

test('canny: imagem plana não gera bordas e limiares altos suprimem', () => {
  assert.ok(vals(canny(criar(5, 5, [10, 10, 10, 255]))).every((v) => v === 0));
  const dados = [];
  for (let y = 0; y < 6; y++) for (let x = 0; x < 6; x++) dados.push(x < 3 ? 100 : 110);
  assert.ok(vals(canny(deCinza(6, 6, dados), { alto: 500, baixo: 400 })).every((v) => v === 0));
});
