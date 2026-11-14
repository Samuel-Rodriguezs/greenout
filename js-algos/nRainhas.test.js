import test from 'node:test';
import assert from 'node:assert/strict';
import { solucoesRainhas, contarRainhas, primeiraSolucao, desenhar } from './nRainhas.js';

test('contagens conhecidas', () => {
  const esperado = [1, 1, 0, 0, 2, 10, 4, 40, 92];
  esperado.forEach((e, n) => assert.equal(contarRainhas(n), e, `n=${n}`));
});
test('n=0 tem a solução vazia', () => assert.deepEqual([...solucoesRainhas(0)], [[]]));
test('sem solução', () => {
  assert.equal(primeiraSolucao(2), null);
  assert.equal(primeiraSolucao(3), null);
});
test('soluções são válidas', () => {
  for (const s of solucoesRainhas(6)) {
    for (let i = 0; i < s.length; i++) for (let j = i + 1; j < s.length; j++) {
      assert.notEqual(s[i], s[j]);
      assert.notEqual(Math.abs(s[i] - s[j]), j - i);
    }
  }
});
test('primeira solução de 4', () => assert.deepEqual(primeiraSolucao(4), [1, 3, 0, 2]));
test('desenho', () => {
  assert.equal(desenhar([1, 3, 0, 2]), '.R..\n...R\nR...\n..R.');
});
test('n inválido', () => {
  assert.throws(() => [...solucoesRainhas(-1)], RangeError);
  assert.throws(() => [...solucoesRainhas(2.5)], RangeError);
});
test('n=10 rápido', () => assert.equal(contarRainhas(10), 724));
