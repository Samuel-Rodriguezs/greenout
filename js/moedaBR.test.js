import { test } from 'node:test';
import assert from 'node:assert/strict';
import { formatarMoeda, lerMoeda } from './moedaBR.js';

test('formata valores comuns', () => {
  assert.equal(formatarMoeda(1234.56), 'R$ 1.234,56');
  assert.equal(formatarMoeda(0), 'R$ 0,00');
  assert.equal(formatarMoeda(5), 'R$ 5,00');
  assert.equal(formatarMoeda(1000000), 'R$ 1.000.000,00');
});

test('valores negativos', () => {
  assert.equal(formatarMoeda(-10.5), '-R$ 10,50');
});

test('arredondamento e zero negativo', () => {
  assert.equal(formatarMoeda(0.004), 'R$ 0,00');
  assert.equal(formatarMoeda(-0.001), 'R$ 0,00');
  assert.equal(formatarMoeda(1.999), 'R$ 2,00');
});

test('rejeita entradas não numéricas', () => {
  assert.throws(() => formatarMoeda('10'), TypeError);
  assert.throws(() => formatarMoeda(NaN), TypeError);
  assert.throws(() => formatarMoeda(Infinity), TypeError);
});

test('lerMoeda interpreta formatos brasileiros', () => {
  assert.equal(lerMoeda('R$ 1.234,56'), 1234.56);
  assert.equal(lerMoeda('1234,5'), 1234.5);
  assert.equal(lerMoeda('-R$ 10,50'), -10.5);
  assert.equal(lerMoeda('1000'), 1000);
});

test('lerMoeda devolve NaN para texto inválido', () => {
  assert.ok(Number.isNaN(lerMoeda('abc')));
  assert.ok(Number.isNaN(lerMoeda('1,2,3')));
  assert.ok(Number.isNaN(lerMoeda('')));
  assert.ok(Number.isNaN(lerMoeda(12)));
});

test('ida e volta', () => {
  assert.equal(lerMoeda(formatarMoeda(98765.43)), 98765.43);
});
