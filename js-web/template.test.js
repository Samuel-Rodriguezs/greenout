import test from 'node:test';
import assert from 'node:assert/strict';
import { compile, tokenize } from './template.js';

test('interpolação simples com escape', () => {
  assert.equal(compile('Olá, {{nome}}!')({ nome: '<b>Ana</b>' }), 'Olá, &lt;b&gt;Ana&lt;/b&gt;!');
});

test('triplas chaves não escapam', () => {
  assert.equal(compile('{{{html}}}')({ html: '<i>x</i>' }), '<i>x</i>');
});

test('caminhos aninhados e ausentes', () => {
  const t = compile('{{user.perfil.cidade}}|{{x.y.z}}');
  assert.equal(t({ user: { perfil: { cidade: 'Recife' } } }), 'Recife|');
});

test('if / else', () => {
  const t = compile('{{#if logado}}sim{{else}}não{{/if}}');
  assert.equal(t({ logado: true }), 'sim');
  assert.equal(t({ logado: false }), 'não');
  assert.equal(compile('{{#if l}}x{{/if}}')({ l: [] }), '');
});

test('each com alias, índice e this', () => {
  assert.equal(compile('{{#each itens as i}}{{index}}:{{i.n}};{{/each}}')({ itens: [{ n: 'a' }, { n: 'b' }] }), '0:a;1:b;');
  assert.equal(compile('{{#each xs}}[{{this}}]{{/each}}')({ xs: [1, 2] }), '[1][2]');
});

test('each acessa contexto externo', () => {
  assert.equal(compile('{{#each xs as x}}{{prefixo}}{{x}} {{/each}}')({ prefixo: '#', xs: [1, 2] }), '#1 #2 ');
});

test('blocos aninhados', () => {
  const t = compile('{{#each xs as x}}{{#if x.ok}}{{x.n}}{{else}}-{{/if}}{{/each}}');
  assert.equal(t({ xs: [{ ok: 1, n: 'a' }, { ok: 0, n: 'b' }] }), 'a-');
});

test('erros de sintaxe', () => {
  assert.throws(() => compile('{{#if a}}x'), /não fechado/);
  assert.throws(() => compile('{{/if}}'), /inesperado/);
});

test('tokenize', () => {
  assert.deepEqual(tokenize('a{{b}}').map((t) => t.type), ['text', 'var']);
});
