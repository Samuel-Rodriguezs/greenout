import test from 'node:test';
import assert from 'node:assert/strict';
import { Conta, TIPOS, reconstruir } from './contaBancaria.js';

test('abrir, depositar e sacar', () => {
  const c = new Conta();
  c.abrir('Ana');
  c.depositar(10000);
  c.sacar(2550);
  assert.equal(c.estado.saldo, 7450);
  assert.deepEqual(c.eventos.map((e) => e.tipo), [TIPOS.ABERTA, TIPOS.DEPOSITO, TIPOS.SAQUE]);
});

test('saldo insuficiente e limite de cheque especial', () => {
  const c = new Conta();
  c.abrir('Bia', 5000);
  c.depositar(1000);
  c.sacar(6000);
  assert.equal(c.estado.saldo, -5000);
  assert.throws(() => c.sacar(1), /insuficiente/);
});

test('reconstruir a partir dos eventos reproduz o estado', () => {
  const c = new Conta();
  c.abrir('Caio');
  c.depositar(500);
  const clone = new Conta(c.eventos);
  assert.deepEqual(clone.estado, c.estado);
  assert.deepEqual(reconstruir(c.eventos), c.estado);
});

test('viagem no tempo', () => {
  const c = new Conta();
  c.abrir('Duda');
  c.depositar(100);
  c.depositar(200);
  c.sacar(50);
  assert.deepEqual([0, 1, 2, 3, 4].map((n) => c.saldoApos(n)), [0, 0, 100, 300, 250]);
});

test('encerramento exige saldo zero e bloqueia operações', () => {
  const c = new Conta();
  c.abrir('Edu');
  c.depositar(100);
  assert.throws(() => c.encerrar(), /zero/);
  c.sacar(100);
  c.encerrar();
  assert.equal(c.estado.aberta, false);
  assert.throws(() => c.depositar(1), /encerrada/);
});

test('validações', () => {
  const c = new Conta();
  assert.throws(() => c.depositar(10), /não foi aberta/);
  c.abrir('Fabi');
  assert.throws(() => c.abrir('Outra'), /já aberta/);
  assert.throws(() => c.depositar(1.5), RangeError);
  assert.throws(() => c.sacar(-1), RangeError);
  assert.throws(() => reconstruir([{ tipo: 'X' }]), /desconhecido/);
});

test('eventos são imutáveis e a lista exposta é cópia', () => {
  const c = new Conta();
  c.abrir('Gui');
  c.eventos.push({ tipo: TIPOS.DEPOSITO, valor: 999 });
  assert.equal(c.eventos.length, 1);
  assert.throws(() => { 'use strict'; c.eventos[0].titular = 'X'; }, TypeError);
});
