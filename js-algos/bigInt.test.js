import test from 'node:test';
import assert from 'node:assert/strict';
import { somar, subtrair, multiplicar, fatorial, potencia, comparar, normalizar, somaDigitos } from './bigInt.js';

test('soma com vai-um em cascata', () => {
  assert.equal(somar('999999999999999999', '1'), '1000000000000000000');
  assert.equal(somar('0', '0'), '0');
  assert.equal(somar('123', '98765432109876543210'), '98765432109876543333');
});
test('subtração', () => {
  assert.equal(subtrair('1000000000000000000', '1'), '999999999999999999');
  assert.equal(subtrair('5', '5'), '0');
  assert.equal(subtrair('100', '1'), '99');
  assert.throws(() => subtrair('1', '2'), RangeError);
});
test('multiplicação', () => {
  assert.equal(multiplicar('0', '12345'), '0');
  assert.equal(multiplicar('1', '12345'), '12345');
  assert.equal(multiplicar('123456789', '987654321'), '121932631112635269');
  assert.equal(multiplicar('99999999999999999999', '99999999999999999999'), '9999999999999999999800000000000000000001');
});
test('confere com BigInt nativo', () => {
  for (let k = 0; k < 100; k++) {
    const a = String(BigInt(Math.floor(Math.random() * 1e15)) * BigInt(Math.floor(Math.random() * 1e15)) + 1n);
    const b = String(BigInt(Math.floor(Math.random() * 1e15)) * 12345678901n);
    assert.equal(somar(a, b), String(BigInt(a) + BigInt(b)));
    assert.equal(multiplicar(a, b), String(BigInt(a) * BigInt(b)));
    if (BigInt(a) >= BigInt(b)) assert.equal(subtrair(a, b), String(BigInt(a) - BigInt(b)));
  }
});
test('fatorial', () => {
  assert.equal(fatorial(0), '1');
  assert.equal(fatorial(1), '1');
  assert.equal(fatorial(20), '2432902008176640000');
  assert.equal(fatorial(30), '265252859812191058636308480000000');
  assert.equal(fatorial(100).length, 158);
  assert.equal(somaDigitos(fatorial(100)), 648);
  assert.throws(() => fatorial(-1), RangeError);
});
test('potência', () => {
  assert.equal(potencia('2', 100), '1267650600228229401496703205376');
  assert.equal(potencia('7', 0), '1');
  assert.equal(potencia('10', 3), '1000');
});
test('comparar e normalizar', () => {
  assert.equal(comparar('10', '9'), 1);
  assert.equal(comparar('007', '7'), 0);
  assert.equal(comparar('1', '2'), -1);
  assert.equal(normalizar('0000'), '0');
  assert.equal(normalizar('0012'), '12');
});
test('entrada inválida', () => {
  assert.throws(() => somar('12a', '1'), TypeError);
  assert.throws(() => multiplicar('', '1'), TypeError);
  assert.throws(() => somar('-1', '1'), TypeError);
});
