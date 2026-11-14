import test from 'node:test';
import assert from 'node:assert/strict';
import { deCinza } from './imagem.js';
import { floydSteinberg, ordenadoBayer, matrizBayer } from './dither.js';

const vals = (img) => Array.from({ length: img.largura * img.altura }, (_, i) => img.dados[i * 4]);
const uniforme = (l, a, v) => deCinza(l, a, new Array(l * a).fill(v));
const brancos = (img) => vals(img).filter((v) => v === 255).length;

test('Floyd-Steinberg 2x2 com cinza 128 (calculado à mão)', () => {
  // (0,0)->255 e=-127 ; (1,0)=128-55.6=72.4->0 ; (0,1)=128-39.7+13.6=101.9->0 ; (1,1)->255
  assert.deepEqual(vals(floydSteinberg(uniforme(2, 2, 128))), [255, 0, 0, 255]);
});

test('Floyd-Steinberg: extremos ficam intactos e saída é binária', () => {
  assert.ok(vals(floydSteinberg(uniforme(4, 4, 0))).every((v) => v === 0));
  assert.ok(vals(floydSteinberg(uniforme(4, 4, 255))).every((v) => v === 255));
  const r = vals(floydSteinberg(deCinza(3, 3, [10, 200, 90, 130, 60, 250, 33, 99, 180])));
  assert.ok(r.every((v) => v === 0 || v === 255));
});

test('Floyd-Steinberg preserva a luminosidade média (~50% de brancos em 128)', () => {
  const n = brancos(floydSteinberg(uniforme(8, 8, 128)));
  assert.ok(n >= 30 && n <= 34, `brancos=${n}`);
  const quarto = brancos(floydSteinberg(uniforme(8, 8, 64)));
  assert.ok(quarto >= 14 && quarto <= 18, `brancos=${quarto}`);
});

test('matrizes de Bayer', () => {
  assert.deepEqual(matrizBayer(2), [[0, 2], [3, 1]]);
  assert.deepEqual(matrizBayer(4), [[0, 8, 2, 10], [12, 4, 14, 6], [3, 11, 1, 9], [15, 7, 13, 5]]);
  const m8 = matrizBayer(8).flat().sort((a, b) => a - b);
  assert.deepEqual(m8, Array.from({ length: 64 }, (_, i) => i));
  assert.throws(() => matrizBayer(3), RangeError);
});

test('Bayer 2x2 com cinza 128: diagonal branca', () => {
  // limiares: 31.9, 159.4 / 223.1, 95.6 -> 128 supera 31.9 e 95.6
  assert.deepEqual(vals(ordenadoBayer(uniforme(2, 2, 128), 2)), [255, 0, 0, 255]);
});

test('Bayer 4x4: quantidade de brancos cresce com o nível', () => {
  // nível v acende os pixels cujo (M+0.5)/16*255 < v ; v=128 -> M+0.5 < 8.03 -> M<=7 -> 8 de 16
  assert.equal(brancos(ordenadoBayer(uniforme(4, 4, 128), 4)), 8);
  assert.equal(brancos(ordenadoBayer(uniforme(4, 4, 0), 4)), 0);
  assert.equal(brancos(ordenadoBayer(uniforme(4, 4, 255), 4)), 16);
  assert.equal(brancos(ordenadoBayer(uniforme(4, 4, 16), 4)), 1); // 16 > 7.97 só para M=0
});
