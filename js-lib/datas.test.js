import { test } from 'node:test';
import assert from 'node:assert/strict';
import { ehBissexto, diasNoMes, addDias, diffDias, inicioDaSemana, formatarISO } from './datas.js';

test('ehBissexto', () => {
  assert.equal(ehBissexto(2024), true);
  assert.equal(ehBissexto(1900), false);
  assert.equal(ehBissexto(2000), true);
  assert.equal(ehBissexto(2023), false);
});
test('diasNoMes', () => {
  assert.equal(diasNoMes(2024, 2), 29);
  assert.equal(diasNoMes(2023, 2), 28);
  assert.equal(diasNoMes(2023, 4), 30);
});
test('addDias cruza mês e ano', () => {
  assert.equal(formatarISO(addDias('2024-12-30T00:00:00Z', 3)), '2025-01-02');
  assert.equal(formatarISO(addDias('2024-03-01T00:00:00Z', -1)), '2024-02-29');
});
test('diffDias', () => {
  assert.equal(diffDias('2024-01-01T00:00:00Z', '2024-03-01T00:00:00Z'), 60);
  assert.equal(diffDias('2024-03-01T00:00:00Z', '2024-01-01T00:00:00Z'), -60);
});
test('inicioDaSemana', () => {
  // 2024-05-15 é quarta-feira
  assert.equal(formatarISO(inicioDaSemana('2024-05-15T10:00:00Z')), '2024-05-12');
  assert.equal(formatarISO(inicioDaSemana('2024-05-15T10:00:00Z', 1)), '2024-05-13');
  assert.equal(formatarISO(inicioDaSemana('2024-05-12T23:00:00Z', 1)), '2024-05-06');
});
