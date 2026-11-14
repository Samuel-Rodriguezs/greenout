import test from 'node:test';
import assert from 'node:assert/strict';
import { deCinza, criar, igual, dePixels, obter } from './imagem.js';
import { nitidez } from './nitidez.js';
import { blurGaussiano } from './gaussiano.js';

const vals = (img) => Array.from({ length: img.largura * img.altura }, (_, i) => img.dados[i * 4]);

test('imagem constante não muda', () => {
  const img = criar(4, 4, [90, 90, 90, 255]);
  assert.ok(igual(nitidez(img, { quantidade: 3 }), img));
});

test('quantidade 0 é identidade', () => {
  const img = deCinza(3, 3, [1, 50, 90, 200, 7, 33, 120, 250, 0]);
  assert.ok(igual(nitidez(img, { quantidade: 0 }), img));
});

test('degrau ganha overshoot nos dois lados', () => {
  const img = deCinza(6, 1, [60, 60, 60, 160, 160, 160]);
  const r = vals(nitidez(img, { sigma: 1, quantidade: 1 }));
  assert.ok(r[2] < 60, 'lado escuro fica mais escuro');
  assert.ok(r[3] > 160, 'lado claro fica mais claro');
  assert.ok(r[0] <= 60 && r[5] >= 160);
});

test('limiar protege diferenças pequenas', () => {
  const img = deCinza(6, 1, [100, 100, 100, 104, 104, 104]);
  assert.ok(igual(nitidez(img, { sigma: 1, quantidade: 5, limiar: 10 }), img));
});

test('fórmula: orig + q*(orig - blur) confere num pixel', () => {
  const img = deCinza(5, 1, [0, 0, 100, 0, 0]);
  const b = obter(blurGaussiano(img, 1), 2, 0)[0];
  // blur arredondado difere <= 0.5 do real; tolerância correspondente (q=2)
  const esperado = 100 + 2 * (100 - b);
  const r = obter(nitidez(img, { sigma: 1, quantidade: 2 }), 2, 0)[0];
  assert.ok(Math.abs(r - Math.min(255, esperado)) <= 1.5, `${r} vs ${esperado}`);
});

test('preserva alfa', () => {
  const img = dePixels(2, 1, [[10, 10, 10, 33], [200, 200, 200, 44]]);
  assert.equal(obter(nitidez(img), 0, 0)[3], 33);
  assert.equal(obter(nitidez(img), 1, 0)[3], 44);
});
