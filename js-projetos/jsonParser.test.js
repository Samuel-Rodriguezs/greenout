import test from 'node:test';
import assert from 'node:assert/strict';
import { parseJson, stringifyJson, ErroJson } from './jsonParser.js';

test('primitivos', () => {
  assert.equal(parseJson('true'), true);
  assert.equal(parseJson(' null '), null);
  assert.equal(parseJson('-12.5e2'), -1250);
  assert.equal(parseJson('"olá"'), 'olá');
});

test('estruturas aninhadas', () => {
  const t = '{"a":[1,2,{"b":null}],"c":{"d":"x"},"e":[]}';
  assert.deepEqual(parseJson(t), { a: [1, 2, { b: null }], c: { d: 'x' }, e: [] });
});

test('escapes de string', () => {
  assert.equal(parseJson('"a\\n\\t\\"\\\\\\u00e9"'), 'a\n\t"\\é');
});

test('concorda com JSON.parse em vários casos válidos', () => {
  for (const t of ['[1,[2,[3]]]', '{"x":{"y":{"z":0.5}}}', '[true,false,null,"s",0,-0.1e-3]', '{}', '[ ]']) {
    assert.deepEqual(parseJson(t), JSON.parse(t));
  }
});

test('rejeita o que JSON.parse também rejeita', () => {
  for (const t of ['', '[1,]', '{"a":1,}', "{'a':1}", '01', '1.', '[1 2]', '"abc', '{"a" 1}', 'nul', '[1]x', '"\\x"', '"\\u12G4"', '{1:2}']) {
    assert.throws(() => parseJson(t), ErroJson, `deveria rejeitar: ${t}`);
    assert.throws(() => JSON.parse(t));
  }
});

test('erro informa a posição', () => {
  try {
    parseJson('[1, 2 3]');
    assert.fail('deveria lançar');
  } catch (e) {
    assert.ok(e instanceof SyntaxError);
    assert.equal(e.posicao, 6);
    assert.match(e.message, /posição 6/);
  }
});

test('chave __proto__ vira propriedade comum', () => {
  const o = parseJson('{"__proto__":1}');
  assert.equal(Object.getPrototypeOf(o), Object.prototype);
  assert.equal(Object.keys(o).length, 1);
});

test('stringify ida e volta, compacto e indentado', () => {
  const v = { a: [1, 'x', null], b: { c: true }, d: undefined, e: NaN };
  assert.equal(stringifyJson(v), '{"a":[1,"x",null],"b":{"c":true},"e":null}');
  assert.equal(stringifyJson(v, 2), JSON.stringify({ a: [1, 'x', null], b: { c: true }, e: null }, null, 2));
  assert.deepEqual(parseJson(stringifyJson(v)), { a: [1, 'x', null], b: { c: true }, e: null });
});
