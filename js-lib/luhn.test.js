import { test } from 'node:test';
import assert from 'node:assert/strict';
import { luhnValido, digitoLuhn, bandeira } from './luhn.js';

test('números válidos', () => {
  assert.ok(luhnValido('4111 1111 1111 1111'));
  assert.ok(luhnValido('5555-5555-5555-4444'));
  assert.ok(luhnValido('378282246310005'));
});
test('inválidos', () => {
  assert.ok(!luhnValido('4111111111111112'));
  assert.ok(!luhnValido('abcd'));
  assert.ok(!luhnValido('123'));
});
test('digitoLuhn completa o número', () => {
  assert.equal(digitoLuhn('411111111111111'), 1);
  assert.ok(luhnValido('411111111111111' + digitoLuhn('411111111111111')));
});
test('bandeira', () => {
  assert.equal(bandeira('4111111111111111'), 'visa');
  assert.equal(bandeira('5555555555554444'), 'mastercard');
  assert.equal(bandeira('378282246310005'), 'amex');
  assert.equal(bandeira('9999'), 'desconhecida');
});
