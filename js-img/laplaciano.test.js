import test from 'node:test';
import assert from 'node:assert/strict';
import { deCinza, criar, obter } from './imagem.js';
import { laplaciano, laplacianoPlano, realcarLaplaciano } from './laplaciano.js';

const vals = (img) => Array.from({ length: img.largura * img.altura }, (_, i) => img.dados[i * 4]);

test('impulso central 3x3 (4-conexo)', () => {
  const p = Float64Array.from([0, 0, 0, 0, 100, 0, 0, 0, 0]);
  assert.deepEqual(Array.from(laplacianoPlano(p, 3, 3, 4)), [0, 100, 0, 100, -400, 100, 0, 100, 0]);
  assert.deepEqual(Array.from(laplacianoPlano(p, 3, 3, 8)), [100, 100, 100, 100, -800, 100, 100, 100, 100]);
});

test('laplaciano em módulo satura em 255', () => {
  const g = deCinza(3, 3, [0, 0, 0, 0, 100, 0, 0, 0, 0]);
  assert.deepEqual(vals(laplaciano(g)), [0, 100, 0, 100, 255, 100, 0, 100, 0]);
});

test('imagem plana e rampa linear têm laplaciano nulo no interior', () => {
  assert.ok(vals(laplaciano(criar(4, 4, [50, 50, 50, 255]))).every((v) => v === 0));
  const rampa = deCinza(5, 3, [0, 10, 20, 30, 40, 0, 10, 20, 30, 40, 0, 10, 20, 30, 40]);
  const l = laplaciano(rampa);
  for (let x = 1; x < 4; x++) assert.equal(obter(l, x, 1)[0], 0);
});

test('conectividade inválida', () => {
  assert.throws(() => laplaciano(criar(2, 2), 6));
});

test('realce aguça o pico e preserva áreas planas', () => {
  const g = deCinza(3, 3, [100, 100, 100, 100, 120, 100, 100, 100, 100]);
  const r = realcarLaplaciano(g);
  // centro: 120 - (4*100 - 4*120) = 120 + 80 = 200 ; vizinhos: 100 - 20 = 80
  assert.equal(obter(r, 1, 1)[0], 200);
  assert.equal(obter(r, 1, 0)[0], 80);
  assert.equal(obter(r, 0, 0)[0], 100);
});
