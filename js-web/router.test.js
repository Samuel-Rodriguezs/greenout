import test from 'node:test';
import assert from 'node:assert/strict';
import { createRouter, parseHash } from './router.js';

const router = createRouter([
  { path: '/', name: 'home', handler: () => 'home' },
  { path: '/usuarios/:id', name: 'usuario', handler: (m) => `u${m.params.id}` },
  { path: '/post/:id/comentario/:cid', name: 'comentario', handler: (m) => m.params },
  { path: '/docs/*', name: 'docs', handler: (m) => m.params['*'] },
], { notFound: () => '404' });

test('parseHash separa caminho e query', () => {
  assert.deepEqual(parseHash('#/a/b/?x=1&y=dois'), { path: 'a/b', query: { x: '1', y: 'dois' } });
});

test('raiz', () => {
  assert.equal(router.resolve('#/'), 'home');
  assert.equal(router.resolve(''), 'home');
});

test('parâmetros dinâmicos', () => {
  assert.equal(router.resolve('#/usuarios/42'), 'u42');
  assert.deepEqual(router.resolve('#/post/1/comentario/9'), { id: '1', cid: '9' });
});

test('decodifica parâmetros', () => {
  assert.equal(router.match('#/usuarios/a%20b').params.id, 'a b');
});

test('wildcard', () => {
  assert.equal(router.resolve('#/docs/a/b/c'), 'a/b/c');
});

test('query string no match', () => {
  assert.deepEqual(router.match('#/usuarios/1?aba=info').query, { aba: 'info' });
});

test('not found', () => {
  assert.equal(router.resolve('#/nada/aqui'), '404');
  assert.equal(createRouter([]).match('#/x'), null);
});

test('href gera link', () => {
  assert.equal(router.href('usuario', { id: 'a b' }), '#/usuarios/a%20b');
  assert.throws(() => router.href('usuario'), /ausente/);
  assert.throws(() => router.href('xx'), /desconhecida/);
});
