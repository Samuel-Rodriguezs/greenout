import { test } from 'node:test';
import assert from 'node:assert/strict';
import { capitalize, camelCase, kebabCase, snakeCase, slugify } from './strings.js';

test('capitalize', () => {
  assert.equal(capitalize('olá MUNDO'), 'Olá mundo');
  assert.equal(capitalize(''), '');
});
test('camelCase', () => {
  assert.equal(camelCase('meu nome-completo_aqui'), 'meuNomeCompletoAqui');
  assert.equal(camelCase('JáEstáAqui'), 'jaEstaAqui');
});
test('kebab e snake', () => {
  assert.equal(kebabCase('helloWorld Foo'), 'hello-world-foo');
  assert.equal(snakeCase('Hello World'), 'hello_world');
});
test('slugify remove acentos e símbolos', () => {
  assert.equal(slugify('  Ação & Reação: Ótimo!  '), 'acao-reacao-otimo');
});
