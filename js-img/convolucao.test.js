import test from 'node:test';
import assert from 'node:assert/strict';
import { deCinza, dePixels, obter, igual } from './imagem.js';
import { convolver, convolverPlano, KERNELS } from './convolucao.js';

const vals = (img) => Array.from({ length: img.largura * img.altura }, (_, i) => img.dados[i * 4]);
const g3 = deCinza(3, 3, [10, 20, 30, 40, 50, 60, 70, 80, 90]);

test('identidade devolve a mesma imagem', () => {
  assert.ok(igual(convolver(g3, KERNELS.identidade), g3));
});

test('média 3x3 no centro e com borda clamp nos cantos', () => {
  const r = convolver(g3, KERNELS.caixa3);
  assert.equal(obter(r, 1, 1)[0], 50);
  // canto (0,0) com clamp: janela [10,10,20 / 10,10,20 / 40,40,50] soma 210 -> 23.33
  assert.equal(obter(r, 0, 0)[0], 23);
  // canto (2,2): [50,60,60 / 80,90,90 / 80,90,90] soma 690 -> 76.67
  assert.equal(obter(r, 2, 2)[0], 77);
});

test('kernel assimétrico é espelhado (convolução, não correlação) e modos de borda', () => {
  const linha = deCinza(4, 1, [1, 2, 3, 4]);
  const k = [[0, 0, 0, 0, 1]]; // out(x) = p(x-2)
  assert.deepEqual(vals(convolver(linha, k, { borda: 'clamp' })), [1, 1, 1, 2]);
  assert.deepEqual(vals(convolver(linha, k, { borda: 'wrap' })), [3, 4, 1, 2]);
  assert.deepEqual(vals(convolver(linha, k, { borda: 'espelho' })), [2, 1, 1, 2]);
  assert.deepEqual(vals(convolver(linha, k, { borda: 'zero' })), [0, 0, 1, 2]);
});

test('divisor, offset e saturação', () => {
  const k = [[1, 1, 1]];
  const linha = deCinza(3, 1, [10, 20, 30]);
  assert.equal(obter(convolver(linha, k, { divisor: 3 }), 1, 0)[0], 20);
  assert.equal(obter(convolver(linha, k, { divisor: 3, offset: 5 }), 1, 0)[0], 25);
  assert.equal(obter(convolver(linha, k), 1, 0)[0], 60);
  assert.equal(obter(convolver(linha, [[10]]), 1, 0)[0], 200);
  assert.equal(obter(convolver(linha, [[20]]), 2, 0)[0], 255);
  assert.throws(() => convolver(linha, k, { divisor: 0 }), RangeError);
});

test('canais independentes e alfa preservado', () => {
  const img = dePixels(3, 1, [[0, 30, 0, 9], [30, 0, 0, 9], [0, 0, 30, 9]]);
  const r = convolver(img, [[1, 0, 0]]); // out(x)=p(x-(-1))? i=0 -> x+1
  assert.deepEqual(obter(r, 0, 0), [30, 0, 0, 9]);
  assert.deepEqual(obter(r, 1, 0), [0, 0, 30, 9]);
});

test('convolverPlano: delta com kernel reproduz o kernel (espelhado)', () => {
  const p = new Float64Array(25);
  p[12] = 1;
  const k = [[1, 2, 3], [4, 5, 6], [7, 8, 9]];
  const r = convolverPlano(p, 5, 5, k, 'zero');
  // Resposta ao impulso reproduz o kernel (sem espelhar)
  assert.deepEqual([r[6], r[7], r[8]], [1, 2, 3]);
  assert.equal(r[12], 5);
  assert.deepEqual([r[16], r[17], r[18]], [7, 8, 9]);
});
