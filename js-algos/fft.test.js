import test from 'node:test';
import assert from 'node:assert/strict';
import { Complexo, fft, ifft, multiplicarPolinomios, espectro } from './fft.js';

const perto = (a, b, eps = 1e-9) => assert.ok(Math.abs(a - b) < eps, `${a} != ${b}`);

test('aritmética complexa', () => {
  const a = new Complexo(1, 2), b = new Complexo(3, -1);
  assert.deepEqual(a.somar(b), new Complexo(4, 1));
  assert.deepEqual(a.subtrair(b), new Complexo(-2, 3));
  assert.deepEqual(a.multiplicar(b), new Complexo(5, 5));
  assert.deepEqual(a.conjugado(), new Complexo(1, -2));
  perto(new Complexo(3, 4).modulo, 5);
  perto(new Complexo(0, 1).fase, Math.PI / 2);
});
test('tamanho 1 e DC', () => {
  assert.equal(fft([5])[0].re, 5);
  const r = fft([1, 1, 1, 1]);
  perto(r[0].re, 4);
  for (let i = 1; i < 4; i++) perto(r[i].modulo, 0);
});
test('impulso tem espectro plano', () => {
  for (const c of fft([1, 0, 0, 0, 0, 0, 0, 0])) { perto(c.re, 1); perto(c.im, 0); }
});
test('DFT conhecida de [1,2,3,4]', () => {
  const r = fft([1, 2, 3, 4]);
  perto(r[0].re, 10);
  perto(r[1].re, -2); perto(r[1].im, 2);
  perto(r[2].re, -2); perto(r[2].im, 0);
  perto(r[3].re, -2); perto(r[3].im, -2);
});
test('inversa recupera o sinal', () => {
  const s = Array.from({ length: 64 }, () => Math.random() * 10 - 5);
  const volta = ifft(fft(s));
  s.forEach((x, i) => { perto(volta[i].re, x, 1e-9); perto(volta[i].im, 0, 1e-9); });
});
test('detecta frequência de um seno', () => {
  const n = 64, f = 5;
  const sinal = Array.from({ length: n }, (_, t) => Math.sin((2 * Math.PI * f * t) / n));
  const esp = espectro(sinal);
  const pico = esp.indexOf(Math.max(...esp.slice(0, n / 2)));
  assert.equal(pico, f);
});
test('tamanho inválido', () => {
  assert.throws(() => fft([1, 2, 3]), RangeError);
  assert.throws(() => fft([]), RangeError);
});
test('multiplicação de polinômios', () => {
  assert.deepEqual(multiplicarPolinomios([1, 1], [1, 1]), [1, 2, 1]);
  assert.deepEqual(multiplicarPolinomios([1, 2, 3], [4, 5]), [4, 13, 22, 15]);
  assert.deepEqual(multiplicarPolinomios([], [1]), []);
  assert.deepEqual(multiplicarPolinomios([7], [6]), [42]);
});
test('polinômios grandes conferem com multiplicação ingênua', () => {
  const p = Array.from({ length: 40 }, () => Math.floor(Math.random() * 10));
  const q = Array.from({ length: 33 }, () => Math.floor(Math.random() * 10));
  const esperado = new Array(72).fill(0);
  p.forEach((a, i) => q.forEach((b, j) => { esperado[i + j] += a * b; }));
  assert.deepEqual(multiplicarPolinomios(p, q), esperado);
});
