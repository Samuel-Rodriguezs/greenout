import test from 'node:test';
import assert from 'node:assert/strict';
import { deCinza, criar, igual, obter } from './imagem.js';
import { vizinhoMaisProximo, bilinear, bicubico, pesosCubicos } from './redimensiona.js';

const vals = (img) => Array.from({ length: img.largura * img.altura }, (_, i) => img.dados[i * 4]);

test('vizinho: ampliar 2x repete cada pixel em bloco 2x2', () => {
  const r = vizinhoMaisProximo(deCinza(2, 2, [1, 2, 3, 4]), 4, 4);
  assert.deepEqual(vals(r), [1, 1, 2, 2, 1, 1, 2, 2, 3, 3, 4, 4, 3, 3, 4, 4]);
});

test('vizinho: reduzir 4 -> 2 amostra os centros em 1 e 3', () => {
  // x = (d+0.5)*2 - 0.5 = 0.5 e 2.5 -> arredonda para 1 e 3
  assert.deepEqual(vals(vizinhoMaisProximo(deCinza(4, 1, [10, 20, 30, 40]), 2, 1)), [20, 40]);
});

test('mesmo tamanho é identidade nos três métodos', () => {
  const g = deCinza(3, 3, [5, 90, 200, 17, 3, 255, 0, 128, 64]);
  assert.ok(igual(vizinhoMaisProximo(g, 3, 3), g));
  assert.ok(igual(bilinear(g, 3, 3), g));
  assert.ok(igual(bicubico(g, 3, 3), g));
});

test('bilinear 2x1 -> 4x1 interpola com clamp nas pontas', () => {
  assert.deepEqual(vals(bilinear(deCinza(2, 1, [0, 100]), 4, 1)), [0, 25, 75, 100]);
});

test('bilinear 2x2 -> 3x3: centro é a média dos quatro', () => {
  const r = bilinear(deCinza(2, 2, [0, 100, 100, 200]), 3, 3);
  // x = (d+0.5)*2/3-0.5: 0 -> -0.17 (clamp), 1 -> 0.5, 2 -> 1.17 (clamp)
  assert.equal(obter(r, 1, 1)[0], 100);
  assert.equal(obter(r, 0, 0)[0], 0);
  assert.equal(obter(r, 2, 2)[0], 200);
  assert.equal(obter(r, 1, 0)[0], 50);
  assert.equal(obter(r, 0, 1)[0], 50);
});

test('bicúbico preserva imagem constante e reproduz rampa linear no interior', () => {
  const c = criar(4, 4, [77, 77, 77, 255]);
  assert.ok(igual(bicubico(c, 8, 8), criar(8, 8, [77, 77, 77, 255])));
  const rampa = deCinza(6, 1, [0, 10, 20, 30, 40, 50]);
  const r = vals(bicubico(rampa, 12, 1));
  // x=3..8 -> posições 1.25 .. 3.75 (sem clamp) : valor esperado = 10*pos
  [12.5, 17.5, 22.5, 27.5, 32.5, 37.5].forEach((esp, i) => assert.ok(Math.abs(r[3 + i] - esp) <= 0.5, `${r[3 + i]} vs ${esp}`));
});

test('pesos cúbicos somam 1 e são interpolantes em t=0', () => {
  for (const t of [0, 0.25, 0.5, 0.9]) assert.ok(Math.abs(pesosCubicos(t).reduce((a, b) => a + b) - 1) < 1e-12);
  assert.deepEqual(pesosCubicos(0).map((v) => Math.round(v * 1e9) / 1e9), [0, 1, 0, 0]);
});

test('tamanho inválido', () => {
  assert.throws(() => bilinear(criar(2, 2), 0, 3), RangeError);
  assert.throws(() => vizinhoMaisProximo(criar(2, 2), 2.5, 3), RangeError);
});
