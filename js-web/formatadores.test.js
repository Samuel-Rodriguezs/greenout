import test from 'node:test';
import assert from 'node:assert/strict';
import {
  formatarNumero, formatarMoeda, formatarPercentual, formatarData,
  tempoRelativo, formatarLista, parseNumeroBR, formatarCompacto,
} from './formatadores.js';

const nb = (s) => s.replace(/\s/g, ' ');

test('número', () => {
  assert.equal(formatarNumero(1234567.891, { casas: 2 }), '1.234.567,89');
  assert.equal(formatarNumero(5, { casas: 2, minCasas: 2 }), '5,00');
});

test('moeda BRL e USD', () => {
  assert.equal(nb(formatarMoeda(1234.5)), 'R$ 1.234,50');
  assert.equal(nb(formatarMoeda(10, 'USD')), 'US$ 10,00');
});

test('percentual', () => {
  assert.equal(nb(formatarPercentual(0.256, 1)), '25,6%');
});

test('compacto', () => {
  assert.match(nb(formatarCompacto(1500000)), /1,5\s?mi/);
});

test('data em fuso de São Paulo', () => {
  assert.equal(formatarData('2024-03-05T12:00:00Z'), '05/03/2024');
  assert.equal(formatarData('2024-03-05T12:00:00Z', 'longa'), '5 de março de 2024');
  assert.equal(nb(formatarData('2024-03-05T15:30:00Z', 'hora')).replace(',', ''), '05/03/2024 12:30');
  assert.throws(() => formatarData(new Date(), 'x'));
});

test('tempo relativo', () => {
  const agora = Date.parse('2024-06-10T12:00:00Z');
  assert.equal(tempoRelativo(agora - 3 * 3600 * 1000, agora), 'há 3 horas');
  assert.equal(tempoRelativo(agora + 86400 * 1000, agora), 'amanhã');
  assert.equal(tempoRelativo(agora - 2 * 86400 * 1000, agora), 'anteontem');
});

test('lista', () => {
  assert.equal(formatarLista(['a', 'b', 'c']), 'a, b e c');
});

test('parseNumeroBR', () => {
  assert.equal(parseNumeroBR('R$ 1.234,56'), 1234.56);
  assert.equal(parseNumeroBR('-12,5'), -12.5);
  assert.ok(Number.isNaN(parseNumeroBR('abc')));
});
