import test from 'node:test';
import assert from 'node:assert/strict';
import { tokenizar, parse, calcular } from './expressoes.js';

test('tokenizar separa números, ids e operadores', () => {
  assert.deepEqual(tokenizar('2.5*x'), [
    { tipo: 'num', valor: 2.5 },
    { tipo: 'op', valor: '*' },
    { tipo: 'id', valor: 'x' },
  ]);
});

test('precedência e parênteses', () => {
  assert.equal(calcular('2 + 3 * 4'), 14);
  assert.equal(calcular('(2 + 3) * 4'), 20);
  assert.equal(calcular('10 - 4 - 3'), 3);
  assert.equal(calcular('100 / 10 / 2'), 5);
});

test('potência associa à direita e unário', () => {
  assert.equal(calcular('2 ^ 3 ^ 2'), 512);
  assert.equal(calcular('-2 ^ 2'), -4);
  assert.equal(calcular('--3'), 3);
  assert.equal(calcular('2 * -3'), -6);
});

test('variáveis e funções', () => {
  assert.equal(calcular('x * 2 + y', { x: 3, y: 1 }), 7);
  assert.equal(calcular('raiz(16) + max(1, 5, 3)'), 9);
  assert.equal(calcular('abs(-4)'), 4);
});

test('estrutura da árvore', () => {
  assert.deepEqual(parse('1+2'), {
    tipo: 'bin', op: '+', esq: { tipo: 'num', valor: 1 }, dir: { tipo: 'num', valor: 2 },
  });
});

test('erros de sintaxe', () => {
  assert.throws(() => calcular('2 +'), SyntaxError);
  assert.throws(() => calcular('(2 + 3'), /Esperado/);
  assert.throws(() => calcular('2 3'), SyntaxError);
  assert.throws(() => calcular('2 $ 3'), /inesperado/);
});

test('erros de avaliação', () => {
  assert.throws(() => calcular('1 / 0'), RangeError);
  assert.throws(() => calcular('z + 1'), ReferenceError);
  assert.throws(() => calcular('foo(1)'), /desconhecida/);
});
