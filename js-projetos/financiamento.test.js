import test from 'node:test';
import assert from 'node:assert/strict';
import { parcelaPrice, tabelaPrice, tabelaSac, resumo, valorFinanciavel } from './financiamento.js';

test('parcela Price conhecida', () => {
  // 100.000 a 1% a.m. por 360 meses ~ 1.028,61
  assert.equal(parcelaPrice(100000, 1, 360), 1028.61);
  assert.equal(parcelaPrice(1200, 0, 12), 100);
});

test('tabela Price quita o saldo e mantém a parcela quase constante', () => {
  const t = tabelaPrice(10000, 2, 12);
  assert.equal(t.length, 12);
  assert.equal(t.at(-1).saldo, 0);
  const fixa = parcelaPrice(10000, 2, 12);
  for (const l of t.slice(0, -1)) assert.equal(l.parcela, fixa);
  assert.ok(Math.abs(t.at(-1).parcela - fixa) < 0.2);
  assert.ok(t[0].juros > t[11].juros);
});

test('amortizações somam o principal', () => {
  const soma = tabelaPrice(5000, 1.5, 10).reduce((s, l) => s + l.amortizacao, 0);
  assert.ok(Math.abs(soma - 5000) < 0.001);
});

test('SAC: amortização constante e parcelas decrescentes', () => {
  const t = tabelaSac(1200, 1, 12);
  assert.equal(t[0].amortizacao, 100);
  assert.equal(t[0].parcela, 112);
  assert.equal(t[11].parcela, 101);
  assert.equal(t.at(-1).saldo, 0);
  for (let k = 1; k < t.length; k++) assert.ok(t[k].parcela < t[k - 1].parcela);
});

test('SAC paga menos juros totais que Price', () => {
  const price = resumo(tabelaPrice(50000, 1.2, 60));
  const sac = resumo(tabelaSac(50000, 1.2, 60));
  assert.ok(sac.totalJuros < price.totalJuros);
  assert.ok(sac.primeiraParcela > price.primeiraParcela);
});

test('sem juros o total pago é o principal', () => {
  const r = resumo(tabelaPrice(1000, 0, 4));
  assert.equal(r.totalPago, 1000);
  assert.equal(r.totalJuros, 0);
});

test('valorFinanciavel é inverso da parcela Price', () => {
  const v = valorFinanciavel(1028.61, 1, 360);
  assert.ok(Math.abs(v - 100000) < 5);
  assert.equal(valorFinanciavel(100, 0, 10), 1000);
});

test('validação de entradas', () => {
  assert.throws(() => parcelaPrice(0, 1, 12), RangeError);
  assert.throws(() => parcelaPrice(100, -1, 12), RangeError);
  assert.throws(() => tabelaSac(100, 1, 0), RangeError);
  assert.throws(() => tabelaSac(100, 1, 2.5), /inteiro/);
});
