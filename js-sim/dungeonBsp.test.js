import test from 'node:test';
import assert from 'node:assert/strict';
import { mulberry32, gerar, regiaoConexa, renderizar } from './dungeonBsp.js';

test('mesma seed gera a mesma dungeon', () => {
  const a = gerar(60, 40, mulberry32(10));
  const b = gerar(60, 40, mulberry32(10));
  assert.equal(renderizar(a.grade), renderizar(b.grade));
  assert.deepEqual(a.salas, b.salas);
  assert.notEqual(renderizar(a.grade), renderizar(gerar(60, 40, mulberry32(11)).grade));
});

test('dimensões da grade e borda externa sempre parede', () => {
  const { grade } = gerar(50, 30, mulberry32(3));
  assert.equal(grade.length, 30);
  assert.ok(grade.every((l) => l.length === 50));
  assert.ok(grade[0].every((v) => v === 0) && grade[29].every((v) => v === 0));
  assert.ok(grade.every((l) => l[0] === 0 && l[49] === 0));
});

test('salas dentro dos limites, com tamanho mínimo e sem sobreposição', () => {
  for (let seed = 1; seed <= 20; seed++) {
    const { salas } = gerar(70, 45, mulberry32(seed));
    assert.ok(salas.length >= 2);
    for (const s of salas) {
      assert.ok(s.x >= 1 && s.y >= 1 && s.x + s.w <= 69 && s.y + s.h <= 44);
      assert.ok(s.w >= 4 && s.h >= 4);
    }
    for (let i = 0; i < salas.length; i++) {
      for (let j = i + 1; j < salas.length; j++) {
        const a = salas[i];
        const b = salas[j];
        const separadas = a.x + a.w <= b.x || b.x + b.w <= a.x || a.y + a.h <= b.y || b.y + b.h <= a.y;
        assert.ok(separadas, `salas ${i} e ${j} sobrepostas (seed ${seed})`);
      }
    }
  }
});

test('todo o chão é conexo (todas as salas ligadas)', () => {
  for (let seed = 1; seed <= 30; seed++) {
    const { grade, salas } = gerar(64, 40, mulberry32(seed));
    const total = grade.flat().filter(Boolean).length;
    const s = salas[0];
    assert.equal(regiaoConexa(grade, s.x, s.y), total, `seed ${seed}`);
  }
});

test('células de sala estão todas como chão', () => {
  const { grade, salas } = gerar(60, 40, mulberry32(4));
  for (const s of salas) for (let y = s.y; y < s.y + s.h; y++) for (let x = s.x; x < s.x + s.w; x++) assert.equal(grade[y][x], 1);
});

test('profundidade 0 gera uma única sala', () => {
  const { salas } = gerar(40, 30, mulberry32(2), { profundidade: 0 });
  assert.equal(salas.length, 1);
});

test('mais profundidade tende a gerar mais salas; mapa pequeno lança erro', () => {
  const poucas = gerar(80, 50, mulberry32(6), { profundidade: 1 }).salas.length;
  const muitas = gerar(80, 50, mulberry32(6), { profundidade: 4 }).salas.length;
  assert.ok(muitas > poucas);
  assert.throws(() => gerar(5, 5, mulberry32(1)));
});

test('regiaoConexa em parede ou fora do mapa é 0', () => {
  assert.equal(regiaoConexa([[0, 1], [1, 1]], 0, 0), 0);
  assert.equal(regiaoConexa([[1]], 5, 5), 0);
  assert.equal(regiaoConexa([[0, 1], [1, 1]], 1, 1), 3);
});
