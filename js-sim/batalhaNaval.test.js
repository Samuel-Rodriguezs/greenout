import test from 'node:test';
import assert from 'node:assert/strict';
import { mulberry32, criarComNavios, criarAleatorio, atirar, venceu, naviosRestantes, FROTA_PADRAO } from './batalhaNaval.js';

test('tiros: água, acerto, afundou, repetido', () => {
  const j = criarComNavios(5, [{ celulas: [[0, 0], [0, 1]] }]);
  assert.equal(atirar(j, 3, 3), 'agua');
  assert.equal(atirar(j, 0, 0), 'acerto');
  assert.equal(atirar(j, 0, 0), 'repetido');
  assert.equal(atirar(j, 0, 1), 'afundou');
  assert.ok(venceu(j));
});

test('naviosRestantes', () => {
  const j = criarComNavios(5, [{ celulas: [[0, 0]] }, { celulas: [[1, 1]] }]);
  assert.equal(naviosRestantes(j), 2);
  atirar(j, 0, 0);
  assert.equal(naviosRestantes(j), 1);
  assert.ok(!venceu(j));
});

test('validações', () => {
  assert.throws(() => criarComNavios(3, [{ celulas: [[3, 0]] }]));
  assert.throws(() => criarComNavios(3, [{ celulas: [[0, 0]] }, { celulas: [[0, 0]] }]));
  const j = criarComNavios(3, []);
  assert.throws(() => atirar(j, -1, 0));
});

test('frota aleatória: tamanhos corretos, sem sobreposição e determinística', () => {
  const j = criarAleatorio(mulberry32(7));
  assert.deepEqual(j.navios.map((n) => n.celulas.length), FROTA_PADRAO);
  const todas = j.navios.flatMap((n) => n.celulas.map(([l, c]) => l + ',' + c));
  assert.equal(new Set(todas).size, todas.length);
  const k = criarAleatorio(mulberry32(7));
  assert.deepEqual(k.navios.map((n) => n.celulas), j.navios.map((n) => n.celulas));
});

test('afundar toda a frota aleatória leva à vitória', () => {
  const j = criarAleatorio(mulberry32(123));
  for (let l = 0; l < 10; l++) for (let c = 0; c < 10; c++) atirar(j, l, c);
  assert.ok(venceu(j));
});

test('frota que não cabe lança erro', () => {
  assert.throws(() => criarAleatorio(mulberry32(1), 3, [5]));
});
