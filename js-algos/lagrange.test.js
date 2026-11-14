import test from 'node:test';
import assert from 'node:assert/strict';
import { lagrange, coeficientes, horner, newton } from './lagrange.js';

const perto = (a, b, eps = 1e-8) => assert.ok(Math.abs(a - b) < eps, `${a} != ${b}`);

test('um ponto dá polinômio constante', () => {
  assert.equal(lagrange([[2, 7]], 100), 7);
  assert.deepEqual(coeficientes([[2, 7]]), [7]);
});
test('reproduz os pontos de entrada', () => {
  const p = [[0, 1], [1, 3], [2, 2], [5, -4]];
  for (const [x, y] of p) perto(lagrange(p, x), y);
});
test('recupera polinômio exato (x^2 - 2x + 3)', () => {
  const p = [-1, 0, 2].map((x) => [x, x * x - 2 * x + 3]);
  perto(lagrange(p, 10), 83);
  const c = coeficientes(p);
  perto(c[0], 3); perto(c[1], -2); perto(c[2], 1);
});
test('coeficientes e Horner concordam com Lagrange', () => {
  const p = [[0, 0], [1, 1], [2, 8], [3, 27]]; // x^3
  const c = coeficientes(p);
  perto(c[3], 1); perto(c[2], 0, 1e-9);
  perto(horner(c, 4), 64);
  perto(lagrange(p, 4), 64);
});
test('Newton equivale a Lagrange', () => {
  const p = [[1, 2], [2, 3], [4, 11], [6, 5]];
  const f = newton(p);
  for (const x of [-1, 0.5, 3, 7]) perto(f(x), lagrange(p, x));
});
test('abscissas repetidas e lista vazia', () => {
  assert.throws(() => lagrange([[1, 1], [1, 2]], 0), RangeError);
  assert.throws(() => coeficientes([]), RangeError);
  assert.throws(() => newton([]), RangeError);
});
test('interpola sen(x) razoavelmente', () => {
  const p = Array.from({ length: 8 }, (_, i) => [i * 0.5, Math.sin(i * 0.5)]);
  perto(lagrange(p, 1.25), Math.sin(1.25), 1e-4);
});
test('horner de polinômio vazio é zero', () => assert.equal(horner([], 5), 0));
