import test from 'node:test';
import assert from 'node:assert/strict';
import { mulberry32, criarJogo, criarComMinas, revelar, alternarBandeira, renderizar } from './campoMinado.js';

test('números ao redor das minas', () => {
  const j = criarComMinas(3, 3, [[0, 0]]);
  assert.deepEqual(j.numeros, [[0, 1, 0], [1, 1, 0], [0, 0, 0]]);
});

test('flood fill revela região de zeros e suas bordas', () => {
  const j = criarComMinas(4, 4, [[0, 0]]);
  revelar(j, 3, 3);
  assert.equal(renderizar(j), ['#1..', '11..', '....', '....'].join('\n'));
  assert.equal(j.status, 'venceu');
});

test('revelar mina perde', () => {
  const j = criarComMinas(3, 3, [[1, 1]]);
  assert.equal(revelar(j, 1, 1), 'perdeu');
  assert.equal(revelar(j, 0, 0), 'perdeu');
});

test('vitória ao revelar todas as seguras', () => {
  const j = criarComMinas(2, 2, [[0, 0]]);
  revelar(j, 0, 1);
  revelar(j, 1, 0);
  assert.equal(j.status, 'jogando');
  assert.equal(revelar(j, 1, 1), 'venceu');
});

test('bandeira bloqueia revelar e pode ser removida', () => {
  const j = criarComMinas(3, 3, [[0, 0]]);
  alternarBandeira(j, 2, 2);
  assert.equal(revelar(j, 2, 2), 'jogando');
  assert.ok(!j.reveladas[2][2]);
  alternarBandeira(j, 2, 2);
  revelar(j, 2, 2);
  assert.ok(j.reveladas[2][2]);
});

test('flood fill não atravessa bandeira', () => {
  const j = criarComMinas(1, 5, [[0, 4]]);
  alternarBandeira(j, 0, 1);
  revelar(j, 0, 0);
  assert.equal(renderizar(j), '.F###');
});

test('primeiro clique nunca é mina e região 3x3 é segura', () => {
  for (let seed = 1; seed <= 30; seed++) {
    const j = criarJogo(9, 9, 10, mulberry32(seed));
    revelar(j, 4, 4);
    assert.notEqual(j.status, 'perdeu');
    assert.equal(j.minas.flat().filter(Boolean).length, 10);
    for (let l = 3; l <= 5; l++) for (let c = 3; c <= 5; c++) assert.ok(!j.minas[l][c]);
    assert.equal(j.numeros[4][4], 0);
  }
});

test('colocação de minas é determinística por seed', () => {
  const a = criarJogo(8, 8, 8, mulberry32(77));
  const b = criarJogo(8, 8, 8, mulberry32(77));
  revelar(a, 0, 0);
  revelar(b, 0, 0);
  assert.deepEqual(a.minas, b.minas);
});
