import test from 'node:test';
import assert from 'node:assert/strict';
import { lzwCodificar, lzwDecodificar } from './lzw.js';

const ida = (t) => lzwDecodificar(lzwCodificar(t));

test('ida e volta', () => {
  for (const t of ['TOBEORNOTTOBEORTOBEORNOT', 'abababababab', 'a', 'aaaaaaaaaa', 'olá, ação! 🎉🎉🎉']) {
    assert.equal(ida(t), t);
  }
});
test('vazio', () => {
  assert.deepEqual(lzwCodificar(''), { alfabeto: [], codigos: [] });
  assert.equal(ida(''), '');
});
test('repetição gera menos códigos que caracteres', () => {
  const t = 'abcabcabcabcabcabc';
  assert.ok(lzwCodificar(t).codigos.length < t.length);
});
test('caso especial cScSc', () => {
  assert.equal(ida('aaaaaaa'), 'aaaaaaa');
  assert.deepEqual(lzwCodificar('aaaaaaa').codigos, [0, 1, 2, 0]);
});
test('códigos inválidos', () => {
  assert.throws(() => lzwDecodificar({ alfabeto: ['a'], codigos: [5] }), RangeError);
  assert.throws(() => lzwDecodificar({ alfabeto: ['a'], codigos: [0, 9] }), RangeError);
});
test('texto longo aleatório', () => {
  const t = Array.from({ length: 3000 }, () => 'abcd'[Math.random() * 4 | 0]).join('');
  assert.equal(ida(t), t);
});
