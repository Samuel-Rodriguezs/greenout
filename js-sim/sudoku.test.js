import test from 'node:test';
import assert from 'node:assert/strict';
import { parse, formatar, podeColocar, gradeConsistente, resolver, resolverTodas, unica } from './sudoku.js';

const PUZZLE = '530070000600195000098000060800060003400803001700020006060000280000419005000080079';
const SOLUCAO = '534678912672195348198342567859761423426853791713924856961537284287419635345286179';

test('parse e formatar são inversos', () => {
  assert.equal(formatar(parse(PUZZLE)), PUZZLE);
  assert.equal(parse('.'.repeat(81))[0][0], 0);
  assert.throws(() => parse('123'));
});

test('podeColocar respeita linha, coluna e bloco', () => {
  const g = parse(PUZZLE);
  assert.ok(!podeColocar(g, 0, 2, 5)); // linha
  assert.ok(!podeColocar(g, 0, 2, 8)); // coluna / bloco
  assert.ok(podeColocar(g, 0, 2, 4));
});

test('resolve puzzle clássico', () => {
  const g = parse(PUZZLE);
  const r = resolver(g);
  assert.equal(formatar(r), SOLUCAO);
  assert.equal(formatar(g), PUZZLE); // entrada intacta
  assert.ok(unica(g));
});

test('puzzle inconsistente ou sem solução retorna null', () => {
  const g = parse(PUZZLE);
  g[0][2] = 5; // duplica 5 na linha
  assert.ok(!gradeConsistente(g));
  assert.equal(resolver(g), null);
  const h = parse('.'.repeat(81));
  // trava a casa (0,0): linha com 1..8 e 9 na coluna
  for (let i = 1; i < 9; i++) h[0][i] = i;
  h[1][0] = 9;
  assert.equal(resolver(h), null);
});

test('grade vazia tem solução válida e várias soluções', () => {
  const g = parse('.'.repeat(81));
  const r = resolver(g);
  assert.ok(r.flat().every((v) => v >= 1 && v <= 9));
  assert.ok(gradeConsistente(r));
  assert.equal(resolverTodas(g, 3).length, 3);
  assert.ok(!unica(g));
});

test('grade já resolvida retorna ela mesma', () => {
  assert.equal(formatar(resolver(parse(SOLUCAO))), SOLUCAO);
});
