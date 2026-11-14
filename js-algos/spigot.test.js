import test from 'node:test';
import assert from 'node:assert/strict';
import { digitosPi, piString, eString } from './spigot.js';

const PI50 = '3.14159265358979323846264338327950288419716939937510';
const E50 = '2.71828182845904523536028747135266249775724709369995';

test('primeiros dígitos de pi', () => {
  const it = digitosPi();
  const ds = Array.from({ length: 10 }, () => it.next().value);
  assert.deepEqual(ds, [3, 1, 4, 1, 5, 9, 2, 6, 5, 3]);
});
test('pi com 51 dígitos', () => assert.equal(piString(51), PI50));
test('pi com 1 e 2 dígitos', () => {
  assert.equal(piString(1), '3');
  assert.equal(piString(2), '3.1');
});
test('pi: 101 dígitos (100 casas) terminam em 3421170679', () => {
  const s = piString(101);
  assert.ok(s.endsWith('8628034825' + '3421170679'));
  assert.equal(s.length, 102);
});
test('e com 50 casas', () => assert.equal(eString(50), E50));
test('e: zero casas e poucas casas', () => {
  assert.equal(eString(0), '2');
  assert.equal(eString(1), '2.7');
  assert.equal(eString(5), '2.71828');
});
test('e: 300 casas conferem com prefixo e comprimento', () => {
  const s = eString(300);
  assert.ok(s.startsWith(E50));
  assert.equal(s.length, 302);
});
test('argumentos inválidos', () => {
  assert.throws(() => piString(0), RangeError);
  assert.throws(() => eString(-1), RangeError);
  assert.throws(() => eString(1.5), RangeError);
});
