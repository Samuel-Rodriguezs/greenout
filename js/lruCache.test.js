import { test } from 'node:test';
import assert from 'node:assert/strict';
import { LRUCache } from './lruCache.js';

test('guarda e recupera valores', () => {
  const c = new LRUCache(2);
  c.set('a', 1).set('b', 2);
  assert.equal(c.get('a'), 1);
  assert.equal(c.get('b'), 2);
  assert.equal(c.get('z'), undefined);
});

test('remove o menos recentemente usado ao exceder a capacidade', () => {
  const c = new LRUCache(2);
  c.set('a', 1).set('b', 2).set('c', 3);
  assert.equal(c.has('a'), false);
  assert.deepEqual(c.chaves(), ['b', 'c']);
});

test('get renova o uso', () => {
  const c = new LRUCache(2);
  c.set('a', 1).set('b', 2);
  c.get('a');
  c.set('c', 3);
  assert.equal(c.has('b'), false);
  assert.equal(c.has('a'), true);
});

test('espiar e has não renovam o uso', () => {
  const c = new LRUCache(2);
  c.set('a', 1).set('b', 2);
  c.espiar('a');
  c.has('a');
  c.set('c', 3);
  assert.equal(c.has('a'), false);
});

test('atualizar chave existente não expulsa ninguém e a renova', () => {
  const c = new LRUCache(2);
  c.set('a', 1).set('b', 2);
  c.set('a', 10);
  assert.equal(c.tamanho, 2);
  assert.deepEqual(c.chaves(), ['b', 'a']);
  assert.equal(c.get('a'), 10);
});

test('capacidade 1', () => {
  const c = new LRUCache(1);
  c.set('a', 1).set('b', 2);
  assert.deepEqual(c.chaves(), ['b']);
});

test('valores falsy são armazenados corretamente', () => {
  const c = new LRUCache(2);
  c.set('zero', 0).set('nulo', null);
  assert.equal(c.get('zero'), 0);
  assert.equal(c.get('nulo'), null);
});

test('delete', () => {
  const c = new LRUCache(2);
  c.set('a', 1);
  assert.equal(c.delete('a'), true);
  assert.equal(c.delete('a'), false);
  assert.equal(c.tamanho, 0);
});

test('capacidade inválida', () => {
  assert.throws(() => new LRUCache(0), RangeError);
  assert.throws(() => new LRUCache(-1), RangeError);
  assert.throws(() => new LRUCache('2'), RangeError);
});
