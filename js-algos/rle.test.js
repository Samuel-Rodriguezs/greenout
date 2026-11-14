import test from 'node:test';
import assert from 'node:assert/strict';
import { rleCodificar, rleDecodificar, rleBytes, rleBytesDecodificar } from './rle.js';

test('codifica', () => {
  assert.equal(rleCodificar('aaabbc'), '3a2b1c');
  assert.equal(rleCodificar(''), '');
  assert.equal(rleCodificar('x'), '1x');
});
test('ida e volta incluindo dígitos e barra', () => {
  for (const t of ['aaabbc', '112233', 'a\\\\b', '', 'zzzzzzzzzzzz', '🎉🎉x']) {
    assert.equal(rleDecodificar(rleCodificar(t)), t);
  }
});
test('quantidades com várias casas', () => {
  const t = 'a'.repeat(123);
  assert.equal(rleCodificar(t), '123a');
  assert.equal(rleDecodificar('123a'), t);
});
test('entrada malformada', () => {
  assert.throws(() => rleDecodificar('abc'), SyntaxError);
  assert.throws(() => rleDecodificar('3'), SyntaxError);
  assert.throws(() => rleDecodificar('3\\'), SyntaxError);
});
test('bytes: limite de 255 por par', () => {
  const dados = new Array(300).fill(7);
  const pares = rleBytes(dados);
  assert.deepEqual(pares, [[7, 255], [7, 45]]);
  assert.deepEqual(rleBytesDecodificar(pares), dados);
});
test('bytes: vazio e alternados', () => {
  assert.deepEqual(rleBytes([]), []);
  assert.deepEqual(rleBytes([1, 2, 1]), [[1, 1], [2, 1], [1, 1]]);
});
