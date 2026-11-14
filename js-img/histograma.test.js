import test from 'node:test';
import assert from 'node:assert/strict';
import { deCinza, dePixels } from './imagem.js';
import { histograma, acumulado, estatisticas, equalizar, esticar } from './histograma.js';

const vals = (img) => Array.from({ length: img.largura * img.altura }, (_, i) => img.dados[i * 4]);

test('histograma conta luma e canais', () => {
  const g = deCinza(3, 3, [0, 0, 0, 10, 10, 20, 255, 255, 255]);
  const h = histograma(g);
  assert.equal(h[0], 3);
  assert.equal(h[10], 2);
  assert.equal(h[20], 1);
  assert.equal(h[255], 3);
  assert.equal(h.reduce((a, b) => a + b), 9);
  const c = dePixels(2, 1, [[5, 6, 7], [5, 0, 7]]);
  assert.equal(histograma(c, 0)[5], 2);
  assert.equal(histograma(c, 1)[6], 1);
});

test('acumulado e estatísticas', () => {
  const h = new Array(256).fill(0);
  h[10] = 2;
  h[30] = 2;
  const c = acumulado(h);
  assert.equal(c[9], 0);
  assert.equal(c[10], 2);
  assert.equal(c[255], 4);
  const e = estatisticas(h);
  assert.equal(e.media, 20);
  assert.equal(e.desvio, 10);
  assert.equal(e.mediana, 10);
});

test('equalizar 2x2 calculado à mão', () => {
  // [0,0,100,200]: cdf(0)=2=cdfmin, cdf(100)=3 -> 1/2*255 = 127.5 -> 128, cdf(200)=4 -> 255
  assert.deepEqual(vals(equalizar(deCinza(2, 2, [0, 0, 100, 200]))), [0, 0, 128, 255]);
});

test('equalizar espalha faixa estreita', () => {
  const g = deCinza(2, 2, [100, 110, 120, 130]);
  // cdf 1,2,3,4 ; cdfmin=1 -> 0, 85, 170, 255
  assert.deepEqual(vals(equalizar(g)), [0, 85, 170, 255]);
});

test('equalizar imagem uniforme não muda', () => {
  const g = deCinza(2, 2, [77, 77, 77, 77]);
  assert.deepEqual(vals(equalizar(g)), [77, 77, 77, 77]);
});

test('esticar leva extremos a 0 e 255', () => {
  assert.deepEqual(vals(esticar(deCinza(2, 2, [50, 100, 150, 200]))), [0, 85, 170, 255]);
});
