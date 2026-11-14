import test from 'node:test';
import assert from 'node:assert/strict';
import { gerarLabirinto, resolver, desenhar, criarRandom } from './labirinto.js';

test('mesma semente gera o mesmo labirinto', () => {
  assert.deepEqual(gerarLabirinto(8, 8, 42), gerarLabirinto(8, 8, 42));
  assert.notDeepEqual(gerarLabirinto(8, 8, 1), gerarLabirinto(8, 8, 2));
});

test('gerador pseudoaleatório fica em [0,1)', () => {
  const r = criarRandom(7);
  for (let i = 0; i < 1000; i++) {
    const v = r();
    assert.ok(v >= 0 && v < 1);
  }
});

test('labirinto é perfeito: conexo e com n-1 passagens', () => {
  const lab = gerarLabirinto(10, 12, 3);
  let passagens = 0;
  for (const linha of lab.celulas) for (const c of linha) passagens += (c.S ? 0 : 1) + (c.L ? 0 : 1);
  assert.equal(passagens, 10 * 12 - 1);
  for (let l = 0; l < 10; l++) {
    for (let c = 0; c < 12; c++) assert.ok(resolver(lab, [0, 0], [l, c]), `inalcançável ${l},${c}`);
  }
});

test('paredes são simétricas e a borda é fechada', () => {
  const lab = gerarLabirinto(6, 6, 9);
  for (let l = 0; l < 6; l++) {
    for (let c = 0; c < 6; c++) {
      if (c < 5) assert.equal(lab.celulas[l][c].L, lab.celulas[l][c + 1].O);
      if (l < 5) assert.equal(lab.celulas[l][c].S, lab.celulas[l + 1][c].N);
    }
    assert.equal(lab.celulas[l][0].O, true);
    assert.equal(lab.celulas[l][5].L, true);
  }
});

test('solução começa na entrada, termina na saída e só dá passos adjacentes', () => {
  const lab = gerarLabirinto(9, 9, 5);
  const s = resolver(lab);
  assert.deepEqual(s[0], [0, 0]);
  assert.deepEqual(s.at(-1), [8, 8]);
  for (let i = 1; i < s.length; i++) {
    assert.equal(Math.abs(s[i][0] - s[i - 1][0]) + Math.abs(s[i][1] - s[i - 1][1]), 1);
  }
});

test('casos pequenos e desenho', () => {
  const um = gerarLabirinto(1, 1);
  assert.deepEqual(resolver(um), [[0, 0]]);
  const lab = gerarLabirinto(2, 3, 1);
  const d = desenhar(lab, resolver(lab));
  assert.equal(d.split('\n').length, 2 * 2 + 2);
  assert.ok(d.includes('()'));
});

test('erros', () => {
  assert.throws(() => gerarLabirinto(0, 5), RangeError);
  assert.throws(() => resolver(gerarLabirinto(3, 3), [0, 0], [9, 9]), /fora/);
});
