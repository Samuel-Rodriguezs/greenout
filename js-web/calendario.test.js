import test from 'node:test';
import assert from 'node:assert/strict';
import {
  diasNoMes, bissexto, gradeDoMes, mesAnterior, mesSeguinte,
  nomeDoMes, cabecalhoSemana, diasUteisEntre, diaDaSemana,
} from './calendario.js';

test('dias no mês e bissexto', () => {
  assert.equal(diasNoMes(2024, 2), 29);
  assert.equal(diasNoMes(2023, 2), 28);
  assert.equal(diasNoMes(2024, 4), 30);
  assert.equal(bissexto(1900), false);
  assert.equal(bissexto(2000), true);
  assert.equal(diaDaSemana(2024, 3, 1), 5);
});

test('grade de março/2024 começando no domingo', () => {
  const g = gradeDoMes(2024, 3);
  assert.equal(g.length, 6);
  assert.ok(g.every((s) => s.length === 7));
  assert.deepEqual(g[0].map((c) => c.data).slice(0, 6), ['2024-02-25', '2024-02-26', '2024-02-27', '2024-02-28', '2024-02-29', '2024-03-01']);
  assert.equal(g[0][0].doMes, false);
  assert.equal(g[0][5].doMes, true);
  assert.equal(g.at(-1).at(-1).data, '2024-04-06');
  assert.equal(g.flat().filter((c) => c.doMes).length, 31);
});

test('semana começando na segunda', () => {
  const g = gradeDoMes(2024, 3, { inicioSemana: 1 });
  assert.equal(g[0][0].data, '2024-02-26');
  assert.equal(g[0][0].fimDeSemana, false);
  assert.equal(g[0][5].fimDeSemana, true);
});

test('mês que começa no primeiro dia da semana não tem folga antes', () => {
  const g = gradeDoMes(2026, 2); // 1/fev/2026 é domingo e tem 28 dias
  assert.equal(g.length, 4);
  assert.equal(g[0][0].data, '2026-02-01');
  assert.equal(g.at(-1).at(-1).data, '2026-02-28');
});

test('hoje e feriados marcados', () => {
  const g = gradeDoMes(2024, 9, { hoje: '2024-09-07', feriados: ['2024-09-07'] });
  const c = g.flat().find((x) => x.data === '2024-09-07');
  assert.equal(c.hoje, true);
  assert.equal(c.feriado, true);
});

test('navegação entre meses', () => {
  assert.deepEqual(mesAnterior(2024, 1), { ano: 2023, mes: 12 });
  assert.deepEqual(mesSeguinte(2024, 12), { ano: 2025, mes: 1 });
  assert.throws(() => gradeDoMes(2024, 13), RangeError);
});

test('nomes localizados', () => {
  assert.equal(nomeDoMes(3), 'março');
  assert.equal(cabecalhoSemana().length, 7);
  assert.match(cabecalhoSemana()[0], /^dom/i);
  assert.match(cabecalhoSemana(1)[0], /^seg/i);
});

test('dias úteis', () => {
  assert.equal(diasUteisEntre('2024-03-04', '2024-03-10'), 5);
  assert.equal(diasUteisEntre('2024-03-09', '2024-03-10'), 0);
});
