import test from 'node:test';
import assert from 'node:assert/strict';
import { renderizar } from './templates.js';

test('substitui variáveis e caminhos', () => {
  assert.equal(renderizar('Olá, {{nome}}!', { nome: 'Ana' }), 'Olá, Ana!');
  assert.equal(renderizar('{{ usuario.endereco.cidade }}', { usuario: { endereco: { cidade: 'Recife' } } }), 'Recife');
});

test('variável ausente vira vazio', () => {
  assert.equal(renderizar('[{{x}}][{{a.b.c}}]', {}), '[][]');
});

test('escapa HTML por padrão e permite bruto', () => {
  assert.equal(renderizar('{{t}}', { t: '<b>"x"</b>' }), '&lt;b&gt;&quot;x&quot;&lt;/b&gt;');
  assert.equal(renderizar('{{{t}}}', { t: '<b>x</b>' }), '<b>x</b>');
});

test('filtros encadeados', () => {
  assert.equal(renderizar('{{n | minuscula | maiuscula}}', { n: 'aBc' }), 'ABC');
  assert.equal(renderizar('{{p | moeda}}', { p: 12.5 }), 'R$ 12,50');
  assert.throws(() => renderizar('{{n | inexistente}}', { n: 1 }), /Filtro desconhecido/);
});

test('condicionais', () => {
  const t = '{{#se logado}}oi {{nome}}{{/se}}';
  assert.equal(renderizar(t, { logado: true, nome: 'Bia' }), 'oi Bia');
  assert.equal(renderizar(t, { logado: false, nome: 'Bia' }), '');
  assert.equal(renderizar('{{#se lista}}x{{/se}}', { lista: [] }), '');
});

test('laços com objetos, primitivos e índice', () => {
  assert.equal(renderizar('{{#cada itens}}<{{nome}}>{{/cada}}', { itens: [{ nome: 'a' }, { nome: 'b' }] }), '<a><b>');
  assert.equal(renderizar('{{#cada xs}}{{indice}}:{{.}} {{/cada}}', { xs: ['p', 'q'] }), '0:p 1:q ');
  assert.equal(renderizar('{{#cada xs}}x{{/cada}}', {}), '');
});

test('bloco não fechado gera erro', () => {
  assert.throws(() => renderizar('{{#se a}}texto', { a: 1 }), /não fechado/);
});
