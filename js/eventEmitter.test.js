import { test } from 'node:test';
import assert from 'node:assert/strict';
import { EventEmitter } from './eventEmitter.js';

test('on + emit entrega argumentos', () => {
  const e = new EventEmitter();
  const recebido = [];
  e.on('x', (a, b) => recebido.push(a, b));
  assert.equal(e.emit('x', 1, 2), true);
  assert.deepEqual(recebido, [1, 2]);
});

test('emit sem ouvintes devolve false', () => {
  assert.equal(new EventEmitter().emit('nada'), false);
});

test('ouvintes são chamados na ordem de registro', () => {
  const e = new EventEmitter();
  const ordem = [];
  e.on('x', () => ordem.push(1)).on('x', () => ordem.push(2));
  e.emit('x');
  assert.deepEqual(ordem, [1, 2]);
});

test('once dispara uma única vez', () => {
  const e = new EventEmitter();
  let n = 0;
  e.once('x', () => n++);
  e.emit('x');
  e.emit('x');
  assert.equal(n, 1);
  assert.equal(e.contarOuvintes('x'), 0);
});

test('off remove um ouvinte específico', () => {
  const e = new EventEmitter();
  let a = 0;
  let b = 0;
  const fa = () => a++;
  e.on('x', fa).on('x', () => b++);
  e.off('x', fa);
  e.emit('x');
  assert.deepEqual([a, b], [0, 1]);
});

test('off sem ouvinte remove todos do evento', () => {
  const e = new EventEmitter();
  e.on('x', () => {}).on('x', () => {});
  e.off('x');
  assert.equal(e.contarOuvintes('x'), 0);
});

test('ouvinte pode se remover durante a emissão sem pular os demais', () => {
  const e = new EventEmitter();
  const visto = [];
  const a = () => { visto.push('a'); e.off('x', a); };
  e.on('x', a).on('x', () => visto.push('b'));
  e.emit('x');
  assert.deepEqual(visto, ['a', 'b']);
});

test('evento "erro" sem ouvinte lança', () => {
  const e = new EventEmitter();
  assert.throws(() => e.emit('erro', new Error('ruim')), /ruim/);
});

test('ouvinte inválido lança TypeError', () => {
  assert.throws(() => new EventEmitter().on('x', 'nao'), TypeError);
});

test('this dentro do ouvinte é o emissor', () => {
  const e = new EventEmitter();
  let alvo;
  e.on('x', function () { alvo = this; });
  e.emit('x');
  assert.equal(alvo, e);
});
