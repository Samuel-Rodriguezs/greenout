import test from 'node:test';
import assert from 'node:assert/strict';
import { Roteador } from './roteador.js';

test('rota estática e raiz', () => {
  const r = new Roteador().get('/', () => 'home').get('/sobre', () => 'sobre');
  assert.equal(r.despachar('GET', '/').corpo, 'home');
  assert.equal(r.despachar('GET', '/sobre/').corpo, 'sobre');
});

test('parâmetros de caminho são extraídos e decodificados', () => {
  const r = new Roteador().get('/usuarios/:id/posts/:slug', ({ params }) => params);
  assert.deepEqual(r.despachar('GET', '/usuarios/42/posts/ol%C3%A1').corpo, { id: '42', slug: 'olá' });
});

test('query string', () => {
  const r = new Roteador().get('/busca', ({ query }) => query);
  assert.deepEqual(r.despachar('GET', '/busca?q=js&pag=2').corpo, { q: 'js', pag: '2' });
});

test('curinga captura o resto', () => {
  const r = new Roteador().get('/arquivos/*', ({ params }) => params['*']);
  assert.equal(r.despachar('GET', '/arquivos/a/b/c.txt').corpo, 'a/b/c.txt');
});

test('primeira rota que casar vence', () => {
  const r = new Roteador().get('/x/novo', () => 'novo').get('/x/:id', () => 'id');
  assert.equal(r.despachar('GET', '/x/novo').corpo, 'novo');
  assert.equal(r.despachar('GET', '/x/7').corpo, 'id');
});

test('404 e 405', () => {
  const r = new Roteador().post('/itens', () => 'criado');
  assert.deepEqual(r.despachar('GET', '/itens'), { status: 405, corpo: 'Método não permitido' });
  assert.equal(r.despachar('GET', '/nada').status, 404);
  assert.equal(r.despachar('post', '/itens').status, 200);
});

test('caracteres especiais no padrão são literais', () => {
  const r = new Roteador().get('/v1.0/ok', () => 'ok');
  assert.equal(r.despachar('GET', '/v1.0/ok').status, 200);
  assert.equal(r.despachar('GET', '/v1x0/ok').status, 404);
});

test('validações', () => {
  const r = new Roteador();
  assert.throws(() => r.get('sem-barra', () => {}), /começar com/);
  assert.throws(() => r.get('/a', null), TypeError);
});
