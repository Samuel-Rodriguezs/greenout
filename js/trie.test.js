import { test } from 'node:test';
import assert from 'node:assert/strict';
import { Trie } from './trie.js';

function criar(...palavras) {
  const t = new Trie();
  palavras.forEach((p) => t.inserir(p));
  return t;
}

test('contem diferencia palavra de prefixo', () => {
  const t = criar('casa', 'casal');
  assert.ok(t.contem('casa'));
  assert.ok(!t.contem('cas'));
  assert.ok(t.temPrefixo('cas'));
  assert.ok(!t.temPrefixo('cb'));
  assert.ok(!t.contem('casas'));
});

test('autocompletar em ordem alfabética', () => {
  const t = criar('carro', 'casa', 'cama', 'casal', 'bola');
  assert.deepEqual(t.autocompletar('ca'), ['cama', 'carro', 'casa', 'casal']);
  assert.deepEqual(t.autocompletar('casa'), ['casa', 'casal']);
  assert.deepEqual(t.autocompletar('x'), []);
});

test('prefixo vazio lista tudo', () => {
  assert.deepEqual(criar('b', 'a').autocompletar(), ['a', 'b']);
});

test('tamanho ignora duplicatas', () => {
  const t = criar('a', 'a', 'ab');
  assert.equal(t.tamanho, 2);
});

test('palavra vazia pode ser inserida', () => {
  const t = criar('');
  assert.ok(t.contem(''));
  assert.equal(t.tamanho, 1);
});

test('suporta acentos e emojis', () => {
  const t = criar('coração', 'ação', '😀a');
  assert.ok(t.contem('coração'));
  assert.deepEqual(t.autocompletar('😀'), ['😀a']);
});

test('remover mantém palavras que compartilham prefixo', () => {
  const t = criar('casa', 'casal');
  assert.equal(t.remover('casal'), true);
  assert.ok(t.contem('casa'));
  assert.ok(!t.temPrefixo('casal'));
  assert.equal(t.tamanho, 1);
});

test('remover palavra que é prefixo de outra', () => {
  const t = criar('casa', 'casal');
  t.remover('casa');
  assert.ok(!t.contem('casa'));
  assert.ok(t.contem('casal'));
});

test('remover inexistente devolve false', () => {
  const t = criar('casa');
  assert.equal(t.remover('cas'), false);
  assert.equal(t.remover('zzz'), false);
  assert.equal(t.tamanho, 1);
});
