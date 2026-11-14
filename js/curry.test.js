import { test } from 'node:test';
import assert from 'node:assert/strict';
import { curry, PLACEHOLDER as _ } from './curry.js';

const soma3 = (a, b, c) => a + b + c;

test('todas as formas de aplicação dão o mesmo resultado', () => {
  const c = curry(soma3);
  assert.equal(c(1)(2)(3), 6);
  assert.equal(c(1, 2)(3), 6);
  assert.equal(c(1)(2, 3), 6);
  assert.equal(c(1, 2, 3), 6);
});

test('aplicação parcial não muta a função original', () => {
  const c = curry(soma3);
  const mais1 = c(1);
  assert.equal(mais1(2)(3), 6);
  assert.equal(mais1(10)(20), 31);
});

test('função de aridade zero executa de imediato', () => {
  assert.equal(curry(() => 42)(), 42);
});

test('aridade explícita para funções variádicas', () => {
  const soma = curry((...n) => n.reduce((a, b) => a + b, 0), 4);
  assert.equal(soma(1)(2)(3)(4), 10);
});

test('placeholder permite pular argumentos', () => {
  const dividir = curry((a, b) => a / b);
  const dividePor2 = dividir(_, 2);
  assert.equal(dividePor2(10), 5);
});

test('preserva this quando todos os argumentos vêm na mesma chamada', () => {
  const obj = { base: 10, f: curry(function (a, b) { return this.base + a + b; }) };
  assert.equal(obj.f(1, 2), 13);
});
