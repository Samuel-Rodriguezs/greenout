import test from 'node:test';
import assert from 'node:assert/strict';
import { simplifica, distanciaPontoSegmento } from './rdp.js';

test('distância ponto-segmento: perpendicular, extremidade e degenerado', () => {
  assert.equal(distanciaPontoSegmento([1, 3], [0, 0], [2, 0]), 3);
  assert.equal(distanciaPontoSegmento([5, 0], [0, 0], [2, 0]), 3);
  assert.equal(distanciaPontoSegmento([3, 4], [0, 0], [0, 0]), 5);
});

test('pontos colineares somem', () => {
  assert.deepEqual(simplifica([[0, 0], [1, 0], [2, 0], [3, 0]], 0.1), [[0, 0], [3, 0]]);
});

test('o pico acima da tolerância é mantido', () => {
  const linha = [[0, 0], [1, 0.05], [2, 3], [3, -0.05], [4, 0]];
  assert.deepEqual(simplifica(linha, 1), [[0, 0], [2, 3], [4, 0]]);
});

test('tolerância grande reduz aos extremos', () => {
  const linha = [[0, 0], [1, 1], [2, 0], [3, 1], [4, 0]];
  assert.deepEqual(simplifica(linha, 10), [[0, 0], [4, 0]]);
});

test('tolerância zero mantém tudo que não é colinear', () => {
  const linha = [[0, 0], [1, 1], [2, 0], [3, 1]];
  assert.deepEqual(simplifica(linha, 0), linha);
});

test('linhas curtas e entrada não alterada', () => {
  assert.deepEqual(simplifica([], 1), []);
  assert.deepEqual(simplifica([[1, 1]], 1), [[1, 1]]);
  const entrada = [[0, 0], [1, 0], [2, 0]];
  const saida = simplifica(entrada, 1);
  saida[0][0] = 99;
  assert.deepEqual(entrada[0], [0, 0]);
});

test('ordem original é preservada em curva longa', () => {
  const linha = Array.from({ length: 101 }, (_, i) => [i, Math.sin(i / 10) * 10]);
  const s = simplifica(linha, 0.2);
  assert.ok(s.length < linha.length && s.length > 4);
  for (let i = 1; i < s.length; i++) assert.ok(s[i][0] > s[i - 1][0]);
  assert.deepEqual(s[0], linha[0]);
  assert.deepEqual(s.at(-1), linha.at(-1));
});

test('tolerância negativa lança erro', () => {
  assert.throws(() => simplifica([[0, 0], [1, 1], [2, 0]], -1), RangeError);
});
