import { test } from 'node:test';
import assert from 'node:assert/strict';
import { fizzbuzz, fizzbuzzDe } from './fizzbuzz.js';

test('limite zero devolve lista vazia', () => {
  assert.deepEqual(fizzbuzz(0), []);
});

test('primeiros 15 valores', () => {
  assert.deepEqual(fizzbuzz(15), [
    '1', '2', 'Fizz', '4', 'Buzz', 'Fizz', '7', '8', 'Fizz', 'Buzz',
    '11', 'Fizz', '13', '14', 'FizzBuzz',
  ]);
});

test('fizzbuzzDe trata múltiplos', () => {
  assert.equal(fizzbuzzDe(30), 'FizzBuzz');
  assert.equal(fizzbuzzDe(9), 'Fizz');
  assert.equal(fizzbuzzDe(25), 'Buzz');
  assert.equal(fizzbuzzDe(7), '7');
});

test('rejeita limite inválido', () => {
  assert.throws(() => fizzbuzz(-1), RangeError);
  assert.throws(() => fizzbuzz(2.5), RangeError);
  assert.throws(() => fizzbuzz('10'), RangeError);
});
