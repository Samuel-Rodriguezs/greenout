import test from 'node:test';
import assert from 'node:assert/strict';
import { bufferLinha } from './bufferLinha.js';
import { area, areaComSinal } from './areaCentroide.js';
import { pontoEmPoligono } from './pontoEmPoligono.js';
import { distanciaPontoSegmento } from './rdp.js';

test('linha reta: área ≈ retângulo + círculo', () => {
  const b = bufferLinha([[0, 0], [10, 0]], 1, { passosTampa: 32 });
  const esperado = 10 * 2 + Math.PI;
  assert.ok(Math.abs(area(b) - esperado) < 0.05, `área ${area(b)}`);
});

test('anel resultante é anti-horário', () => {
  assert.ok(areaComSinal(bufferLinha([[0, 0], [5, 5], [10, 0]], 1)) > 0);
  assert.ok(areaComSinal(bufferLinha([[10, 0], [0, 0]], 1)) > 0);
});

test('todos os pontos da linha ficam dentro do buffer', () => {
  const linha = [[0, 0], [10, 0], [10, 10], [0, 10]];
  const b = bufferLinha(linha, 2);
  for (const p of linha) assert.equal(pontoEmPoligono(p, b), true);
  assert.equal(pontoEmPoligono([5, 0], b), true);
  assert.equal(pontoEmPoligono([5, 5], b), false);
  assert.equal(pontoEmPoligono([5, 2.5], b), false);
});

test('vértices do buffer de linha reta ficam a distância d da linha', () => {
  const linha = [[0, 0], [10, 0]];
  const b = bufferLinha(linha, 3);
  for (const v of b) {
    assert.ok(Math.abs(distanciaPontoSegmento(v, linha[0], linha[1]) - 3) < 1e-9);
  }
});

test('ponto isolado vira um polígono aproximando o círculo', () => {
  const b = bufferLinha([[5, 5]], 2, { passosTampa: 16 });
  assert.ok(Math.abs(area(b) - Math.PI * 4) < 0.3);
});

test('pontos repetidos consecutivos são ignorados', () => {
  const a = bufferLinha([[0, 0], [0, 0], [4, 0]], 1);
  const b = bufferLinha([[0, 0], [4, 0]], 1);
  assert.deepEqual(a, b);
});

test('distância inválida e linha vazia lançam erro', () => {
  assert.throws(() => bufferLinha([[0, 0], [1, 1]], 0), RangeError);
  assert.throws(() => bufferLinha([[0, 0], [1, 1]], -1), RangeError);
  assert.throws(() => bufferLinha([], 1), RangeError);
});
