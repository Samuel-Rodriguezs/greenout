import test from 'node:test';
import assert from 'node:assert/strict';
import { distanciaEdicao, operacoesEdicao } from './editDistance.js';

test('clássicos', () => {
  assert.equal(distanciaEdicao('kitten', 'sitting'), 3);
  assert.equal(distanciaEdicao('sunday', 'saturday'), 3);
});
test('vazios', () => {
  assert.equal(distanciaEdicao('', ''), 0);
  assert.equal(distanciaEdicao('', 'abc'), 3);
  assert.equal(distanciaEdicao('abcd', ''), 4);
});
test('iguais e simetria', () => {
  assert.equal(distanciaEdicao('abc', 'abc'), 0);
  assert.equal(distanciaEdicao('flaw', 'lawn'), distanciaEdicao('lawn', 'flaw'));
});
test('acentos contam como caractere', () => {
  assert.equal(distanciaEdicao('coração', 'coracao'), 2);
});
test('operações aplicadas geram o destino', () => {
  const a = 'intention', b = 'execution';
  const ops = operacoesEdicao(a, b);
  const custo = ops.filter((o) => o.op !== 'manter').length;
  assert.equal(custo, distanciaEdicao(a, b));
  let r = '';
  for (const o of ops) {
    if (o.op === 'manter' || o.op === 'inserir') r += o.char;
    else if (o.op === 'trocar') r += o.para;
  }
  assert.equal(r, b);
});
test('operações com vazio', () => {
  assert.deepEqual(operacoesEdicao('', 'ab').map((o) => o.op), ['inserir', 'inserir']);
  assert.deepEqual(operacoesEdicao('ab', '').map((o) => o.op), ['remover', 'remover']);
  assert.deepEqual(operacoesEdicao('', ''), []);
});
