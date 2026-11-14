import test from 'node:test';
import assert from 'node:assert/strict';
import { criarFormiga, passo, simular, contarPretas, renderizar } from './formigaLangton.js';

test('primeiro passo: vira à direita, pinta e avança', () => {
  const f = criarFormiga(5, 5);
  passo(f);
  assert.equal(f.grade[2][2], 1);
  assert.equal(f.dir, 1);
  assert.deepEqual([f.x, f.y], [3, 2]);
});

test('quatro primeiros passos desenham um quadrado', () => {
  const f = simular(criarFormiga(5, 5), 4);
  assert.equal(contarPretas(f), 4);
  assert.deepEqual([f.x, f.y], [2, 2]);
  assert.equal(f.dir, 0);
});

test('o passo seguinte volta a uma célula preta e vira à esquerda', () => {
  const f = simular(criarFormiga(5, 5), 5);
  assert.equal(f.passos, 5);
  assert.equal(f.grade[2][2], 0);
  assert.equal(contarPretas(f), 3);
});

test('paridade: nº de pretas tem a paridade do nº de passos', () => {
  const f = criarFormiga(21, 21);
  for (let i = 1; i <= 300; i++) {
    passo(f);
    assert.equal(contarPretas(f) % 2, i % 2);
  }
});

test('toroidal: sai por uma borda e entra pela oposta', () => {
  const f = criarFormiga(3, 3, 2, 0, 0);
  f.grade[0][2] = 1; // preta: vira à esquerda (dir 3) e anda para x=1
  passo(f);
  assert.deepEqual([f.x, f.y], [1, 0]);
  const g = criarFormiga(3, 3, 0, 0, 3);
  passo(g); // branca: vira à direita (dir 0, cima) e vai para y=2
  assert.deepEqual([g.x, g.y], [0, 2]);
});

test('determinismo e renderização', () => {
  const a = simular(criarFormiga(15, 15), 200);
  const b = simular(criarFormiga(15, 15), 200);
  assert.equal(renderizar(a), renderizar(b));
  assert.equal(renderizar(criarFormiga(3, 3)).split('\n')[1], '.@.');
});
