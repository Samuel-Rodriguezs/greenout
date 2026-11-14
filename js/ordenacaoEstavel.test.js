import { test } from 'node:test';
import assert from 'node:assert/strict';
import { ordenarEstavel, ordenarPor } from './ordenacaoEstavel.js';

test('ordena números (ao contrário do sort padrão, que compara strings)', () => {
  assert.deepEqual(ordenarEstavel([10, 9, 1, 100]), [1, 9, 10, 100]);
});

test('não muta a entrada', () => {
  const original = [3, 1, 2];
  const r = ordenarEstavel(original);
  assert.deepEqual(original, [3, 1, 2]);
  assert.notEqual(r, original);
});

test('vazio e um elemento', () => {
  assert.deepEqual(ordenarEstavel([]), []);
  assert.deepEqual(ordenarEstavel([7]), [7]);
});

test('é estável em empates', () => {
  const itens = [
    { n: 'a', v: 2 }, { n: 'b', v: 1 }, { n: 'c', v: 2 },
    { n: 'd', v: 1 }, { n: 'e', v: 2 },
  ];
  const r = ordenarEstavel(itens, (x, y) => x.v - y.v);
  assert.deepEqual(r.map((i) => i.n), ['b', 'd', 'a', 'c', 'e']);
});

test('comparador customizado (decrescente)', () => {
  assert.deepEqual(ordenarEstavel([1, 3, 2], (a, b) => b - a), [3, 2, 1]);
});

test('ordenarPor com múltiplas chaves e ordem decrescente', () => {
  const gente = [
    { nome: 'Ana', idade: 30 },
    { nome: 'Bia', idade: 25 },
    { nome: 'Caio', idade: 30 },
    { nome: 'Davi', idade: 25 },
  ];
  assert.deepEqual(
    ordenarPor(gente, '-idade', 'nome').map((p) => p.nome),
    ['Ana', 'Caio', 'Bia', 'Davi'],
  );
  assert.deepEqual(
    ordenarPor(gente, 'idade', '-nome').map((p) => p.nome),
    ['Davi', 'Bia', 'Caio', 'Ana'],
  );
});

test('resultado coincide com Array.prototype.sort em dados aleatórios', () => {
  let semente = 12345;
  const aleatorio = () => (semente = (semente * 1103515245 + 12345) % 2147483648);
  const dados = Array.from({ length: 500 }, () => aleatorio() % 50);
  assert.deepEqual(ordenarEstavel(dados), [...dados].sort((a, b) => a - b));
});
