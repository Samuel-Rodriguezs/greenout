import test from 'node:test';
import assert from 'node:assert/strict';
import { codificar, decodificar, construirArvore, tabelaCodigos } from './huffman.js';

test('ida e volta', () => {
  for (const t of ['abracadabra', 'huffman coding é legal', 'aaaaaaa', 'ab', 'a']) {
    const { bits, arvore } = codificar(t);
    assert.equal(decodificar(bits, arvore), t);
  }
});
test('texto vazio', () => {
  const { bits, arvore } = codificar('');
  assert.equal(bits, '');
  assert.equal(arvore, null);
  assert.equal(decodificar('', null), '');
});
test('comprime texto repetitivo', () => {
  const t = 'aaaaaaaaaabbbbbcd';
  const { bits } = codificar(t);
  assert.ok(bits.length < t.length * 8);
});
test('símbolo mais frequente tem código mais curto', () => {
  const tab = tabelaCodigos(construirArvore('aaaaaabbbc'));
  assert.ok(tab.get('a').length <= tab.get('b').length);
  assert.ok(tab.get('b').length <= tab.get('c').length);
});
test('códigos são livres de prefixo', () => {
  const cods = [...tabelaCodigos(construirArvore('the quick brown fox')).values()];
  for (const x of cods) for (const y of cods) if (x !== y) assert.equal(y.startsWith(x), false);
});
test('um único símbolo usa 1 bit por ocorrência', () => {
  assert.equal(codificar('zzzz').bits, '0000');
});
test('bits inválidos ou truncados', () => {
  const { arvore } = codificar('abcabcaa');
  assert.throws(() => decodificar('2', arvore), SyntaxError);
  const cod = [...tabelaCodigos(arvore).values()].find((c) => c.length > 1);
  assert.throws(() => decodificar(cod.slice(0, -1), arvore), SyntaxError);
});
