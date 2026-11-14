import test from 'node:test';
import assert from 'node:assert/strict';
import {
  literal, regex, mapear, sequencia, ou, muitos, umOuMais, opcional, separadoPor, token,
  analisar, calculadora, parserJson,
} from './parserCombinators.js';

test('literal e regex', () => {
  assert.deepEqual(literal('ab')('abc', 0), { ok: true, valor: 'ab', pos: 2 });
  assert.equal(literal('x')('abc', 0).ok, false);
  assert.deepEqual(regex(/\d+/)('12ab', 0), { ok: true, valor: '12', pos: 2 });
  assert.equal(regex(/\d+/)('ab12', 0).ok, false); // ancorado
  assert.deepEqual(regex(/\d+/)('ab12', 2).valor, '12');
});
test('sequencia, mapear e falha no meio', () => {
  const p = mapear(sequencia(literal('a'), literal('b')), ([x, y]) => x + y + '!');
  assert.equal(p('ab', 0).valor, 'ab!');
  const falhou = sequencia(literal('a'), literal('b'))('ac', 0);
  assert.equal(falhou.ok, false);
  assert.equal(falhou.pos, 1);
});
test('ou escolhe a primeira que casa e combina mensagens de erro', () => {
  assert.equal(ou(literal('a'), literal('b'))('b', 0).valor, 'b');
  const r = ou(literal('a'), literal('b'))('c', 0);
  assert.equal(r.ok, false);
  assert.match(r.esperado, /"a" ou "b"/);
});
test('muitos, umOuMais e opcional', () => {
  assert.deepEqual(muitos(literal('a'))('aaab', 0), { ok: true, valor: ['a', 'a', 'a'], pos: 3 });
  assert.deepEqual(muitos(literal('a'))('b', 0).valor, []);
  assert.equal(umOuMais(literal('a'))('b', 0).ok, false);
  assert.equal(opcional(literal('x'), 'padrao')('y', 0).valor, 'padrao');
  // parser que não consome não pode gerar laço infinito
  assert.deepEqual(muitos(opcional(literal('x')))('y', 0).valor, []);
});
test('separadoPor', () => {
  const lista = separadoPor(regex(/\d/), literal(','));
  assert.deepEqual(lista('1,2,3', 0).valor, ['1', '2', '3']);
  assert.deepEqual(lista('', 0).valor, []);
  assert.equal(lista('1,', 0).ok, false); // separador pendurado
});
test('analisar exige consumir tudo e reporta posição', () => {
  const p = token(regex(/\d+/));
  assert.equal(analisar(p, ' 42 '), '42');
  assert.throws(() => analisar(p, '42 x'), /posição 3: esperado fim da entrada/);
});
test('calculadora: precedência, associatividade e parênteses', () => {
  const calc = calculadora();
  assert.equal(calc('1 + 2 * 3'), 7);
  assert.equal(calc('(1 + 2) * 3'), 9);
  assert.equal(calc('10 - 4 - 3'), 3);
  assert.equal(calc('100 / 10 / 5'), 2);
  assert.equal(calc('2 ^ 3 ^ 2'), 512);
  assert.equal(calc('-3 + 5'), 2);
  assert.equal(calc('2 * -3'), -6);
  assert.equal(calc('1.5 * 2'), 3);
  assert.equal(calc('  7  '), 7);
});
test('calculadora: erros de sintaxe', () => {
  const calc = calculadora();
  assert.throws(() => calc(''), SyntaxError);
  assert.throws(() => calc('1 +'), SyntaxError);
  assert.throws(() => calc('(1 + 2'), SyntaxError);
  assert.throws(() => calc('1 2'), SyntaxError);
});
test('json: valores simples', () => {
  const json = parserJson();
  assert.equal(json('null'), null);
  assert.equal(json(' true '), true);
  assert.equal(json('false'), false);
  assert.equal(json('-12.5e1'), -125);
  assert.equal(json('"olá \\"mundo\\"\\n"'), 'olá "mundo"\n');
});
test('json: estruturas aninhadas confere com JSON.parse', () => {
  const json = parserJson();
  const textos = [
    '[]', '{}', '[1, 2, [3, [4]]]',
    '{"a": 1, "b": [true, null], "c": {"d": "x"}}',
    ' { "k" : [ { "z" : 0 } ] } ',
  ];
  for (const t of textos) assert.deepEqual(json(t), JSON.parse(t));
});
test('json: entradas inválidas', () => {
  const json = parserJson();
  for (const t of ['', '[1,]', '{"a" 1}', '[1 2]', '{"a":}', 'nul']) {
    assert.throws(() => json(t), SyntaxError, t);
  }
});
