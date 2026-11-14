import test from 'node:test';
import assert from 'node:assert/strict';
import { maiorPalindromo, contarPalindromos, ehPalindromo } from './manacher.js';

test('bordas', () => {
  assert.equal(maiorPalindromo(''), '');
  assert.equal(maiorPalindromo('a'), 'a');
  assert.equal(contarPalindromos(''), 0);
});
test('tamanho par e ímpar', () => {
  assert.equal(maiorPalindromo('babad'), 'bab');
  assert.equal(maiorPalindromo('cbbd'), 'bb');
  assert.equal(maiorPalindromo('forgeeksskeegfor'), 'geeksskeeg');
});
test('sem repetição: primeiro caractere', () => assert.equal(maiorPalindromo('abcd'), 'a'));
test('string inteira palíndroma', () => assert.equal(maiorPalindromo('racecar'), 'racecar'));
test('contagem de palíndromos', () => {
  assert.equal(contarPalindromos('aaa'), 6);
  assert.equal(contarPalindromos('abc'), 3);
  assert.equal(contarPalindromos('abba'), 6);
});
test('ehPalindromo', () => {
  assert.equal(ehPalindromo('arara'), true);
  assert.equal(ehPalindromo('ab'), false);
  assert.equal(ehPalindromo(''), true);
});
test('confere com força bruta', () => {
  const bruto = (s) => {
    let m = 0;
    for (let i = 0; i < s.length; i++) for (let j = i; j < s.length; j++) {
      const t = s.slice(i, j + 1);
      if (t === [...t].reverse().join('') && t.length > m) m = t.length;
    }
    return m;
  };
  for (let k = 0; k < 50; k++) {
    const s = Array.from({ length: 12 }, () => 'abc'[Math.random() * 3 | 0]).join('');
    assert.equal(maiorPalindromo(s).length, bruto(s));
  }
});
