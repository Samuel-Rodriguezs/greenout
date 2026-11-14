import { test } from 'node:test';
import assert from 'node:assert/strict';
import { decimalParaBinario, binarioParaDecimal } from './binario.js';

test('decimal para binário', () => {
  assert.equal(decimalParaBinario(0), '0');
  assert.equal(decimalParaBinario(1), '1');
  assert.equal(decimalParaBinario(10), '1010');
  assert.equal(decimalParaBinario(255), '11111111');
  assert.equal(decimalParaBinario(-5), '-101');
});

test('binário para decimal', () => {
  assert.equal(binarioParaDecimal('0'), 0);
  assert.equal(binarioParaDecimal('1010'), 10);
  assert.equal(binarioParaDecimal('0001'), 1);
  assert.equal(binarioParaDecimal('-101'), -5);
});

test('coincide com toString(2) e parseInt para vários valores', () => {
  for (const n of [2, 7, 8, 1023, 1024, 65535, 2 ** 40, Number.MAX_SAFE_INTEGER]) {
    assert.equal(decimalParaBinario(n), n.toString(2));
    assert.equal(binarioParaDecimal(n.toString(2)), n);
  }
});

test('ida e volta com negativos', () => {
  for (let n = -64; n <= 64; n++) {
    assert.equal(binarioParaDecimal(decimalParaBinario(n)), n);
  }
});

test('entradas inválidas', () => {
  assert.throws(() => decimalParaBinario(1.5), RangeError);
  assert.throws(() => decimalParaBinario(NaN), RangeError);
  assert.throws(() => decimalParaBinario('3'), RangeError);
  assert.throws(() => binarioParaDecimal(''), SyntaxError);
  assert.throws(() => binarioParaDecimal('102'), SyntaxError);
  assert.throws(() => binarioParaDecimal('-'), SyntaxError);
  assert.throws(() => binarioParaDecimal(101), SyntaxError);
});

test('valor grande demais para inteiro seguro', () => {
  assert.throws(() => binarioParaDecimal('1'.repeat(60)), RangeError);
});
