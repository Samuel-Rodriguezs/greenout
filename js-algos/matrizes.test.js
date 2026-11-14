import test from 'node:test';
import assert from 'node:assert/strict';
import { determinante, resolverSistema, inversa, identidade, multiplicarMatrizes, transposta, posto } from './matrizes.js';

const perto = (a, b, eps = 1e-9) => assert.ok(Math.abs(a - b) < eps, `${a} != ${b}`);

test('determinante', () => {
  perto(determinante([[5]]), 5);
  perto(determinante([[1, 2], [3, 4]]), -2);
  perto(determinante([[2, 0, 1], [1, 3, 2], [1, 1, 1]]), 2 * (3 - 2) - 0 + 1 * (1 - 3));
  perto(determinante(identidade(5)), 1);
});
test('determinante de singular é zero e troca de linha muda sinal', () => {
  assert.equal(determinante([[1, 2], [2, 4]]), 0);
  perto(determinante([[0, 1], [1, 0]]), -1);
});
test('matriz inválida', () => {
  assert.throws(() => determinante([]), RangeError);
  assert.throws(() => determinante([[1, 2]]), RangeError);
});
test('resolve sistema 3x3', () => {
  const x = resolverSistema([[2, 1, -1], [-3, -1, 2], [-2, 1, 2]], [8, -11, -3]);
  perto(x[0], 2); perto(x[1], 3); perto(x[2], -1);
});
test('sistema que exige pivoteamento (pivô zero)', () => {
  const x = resolverSistema([[0, 1], [1, 0]], [3, 4]);
  assert.deepEqual(x.map((v) => Math.round(v)), [4, 3]);
});
test('sistema singular e dimensões erradas', () => {
  assert.throws(() => resolverSistema([[1, 2], [2, 4]], [1, 2]), /singular/);
  assert.throws(() => resolverSistema([[1]], [1, 2]), RangeError);
});
test('inversa: A * A^-1 = I', () => {
  const A = [[4, 7, 2], [3, 6, 1], [2, 5, 3]];
  const prod = multiplicarMatrizes(A, inversa(A));
  prod.forEach((l, i) => l.forEach((v, j) => perto(v, i === j ? 1 : 0)));
  assert.throws(() => inversa([[1, 1], [1, 1]]), /singular/);
});
test('multiplicação e transposta', () => {
  assert.deepEqual(multiplicarMatrizes([[1, 2], [3, 4]], [[5, 6], [7, 8]]), [[19, 22], [43, 50]]);
  assert.deepEqual(transposta([[1, 2, 3], [4, 5, 6]]), [[1, 4], [2, 5], [3, 6]]);
  assert.throws(() => multiplicarMatrizes([[1, 2]], [[1, 2]]), RangeError);
});
test('posto', () => {
  assert.equal(posto([[1, 2], [2, 4]]), 1);
  assert.equal(posto(identidade(4)), 4);
  assert.equal(posto([[1, 2, 3], [4, 5, 6]]), 2);
  assert.equal(posto([[0, 0], [0, 0]]), 0);
});
test('não altera a matriz de entrada', () => {
  const m = [[1, 2], [3, 4]];
  determinante(m); inversa(m);
  assert.deepEqual(m, [[1, 2], [3, 4]]);
});
