import test from 'node:test';
import assert from 'node:assert/strict';
import { mulberry32, exponencial, gerarClientes, simularClientes, simular } from './filaAtendimento.js';

const tres = [
  { id: 1, chegada: 0, servico: 3 },
  { id: 2, chegada: 1, servico: 3 },
  { id: 3, chegada: 2, servico: 3 },
];

test('um guichê: esperas crescem e fila máxima é 2', () => {
  const r = simularClientes(tres, 1);
  assert.deepEqual(r.atendimentos.map((a) => a.espera), [0, 2, 4]);
  assert.equal(r.esperaMedia, 2);
  assert.equal(r.esperaMaxima, 4);
  assert.equal(r.tamanhoMaximoFila, 2);
  assert.equal(r.tempoTotal, 9);
  assert.equal(r.ocupacao, 1);
});

test('três guichês: ninguém espera', () => {
  const r = simularClientes(tres, 3);
  assert.equal(r.esperaMaxima, 0);
  assert.equal(r.tamanhoMaximoFila, 0);
  assert.deepEqual(r.atendimentos.map((a) => a.guiche), [0, 1, 2]);
  assert.ok(Math.abs(r.ocupacao - 9 / (5 * 3)) < 1e-12);
});

test('dois guichês: terceiro cliente espera o primeiro liberar', () => {
  const r = simularClientes(tres, 2);
  assert.deepEqual(r.atendimentos.map((a) => a.espera), [0, 0, 1]);
  assert.equal(r.atendimentos[2].guiche, 0);
});

test('entrada fora de ordem é ordenada por chegada', () => {
  const r = simularClientes([...tres].reverse(), 1);
  assert.deepEqual(r.atendimentos.map((a) => a.id), [1, 2, 3]);
});

test('sem clientes e guichês inválidos', () => {
  const r = simularClientes([], 2);
  assert.equal(r.atendidos, 0);
  assert.equal(r.ocupacao, 0);
  assert.throws(() => simularClientes(tres, 0));
});

test('exponencial tem média próxima da esperada', () => {
  const rng = mulberry32(2024);
  let soma = 0;
  const n = 20000;
  for (let i = 0; i < n; i++) soma += exponencial(rng, 5);
  assert.ok(Math.abs(soma / n - 5) < 0.2);
});

test('geração de clientes é determinística e respeita a duração', () => {
  const cfg = { mediaChegada: 2, mediaServico: 1.5, duracao: 100 };
  const a = gerarClientes(mulberry32(5), cfg);
  const b = gerarClientes(mulberry32(5), cfg);
  assert.deepEqual(a, b);
  assert.ok(a.length > 20 && a.every((c) => c.chegada <= 100));
  assert.ok(a.every((c, i) => i === 0 || c.chegada >= a[i - 1].chegada));
});

test('mais guichês reduzem a espera média (mesma carga)', () => {
  const cfg = { mediaChegada: 1, mediaServico: 1.8, duracao: 500 };
  const e = [1, 2, 3, 4].map((g) => simular(mulberry32(1), cfg, g).esperaMedia);
  for (let i = 1; i < e.length; i++) assert.ok(e[i] <= e[i - 1]);
  assert.ok(e[0] > e[3]);
});
