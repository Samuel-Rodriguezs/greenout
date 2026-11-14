import test from 'node:test';
import assert from 'node:assert/strict';
import { aEstrela, lerMapa } from './astar.js';

function mulberry32(seed) {
  let a = seed >>> 0;
  return () => {
    a = (a + 0x6d2b79f5) >>> 0;
    let t = a;
    t = Math.imul(t ^ (t >>> 15), t | 1);
    t ^= t + Math.imul(t ^ (t >>> 7), t | 61);
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}

// BFS de referência para comparar o comprimento ótimo em 4 direções
function bfs(grade, ini, fim) {
  const dist = new Map([[ini.join(), 0]]);
  const fila = [ini];
  while (fila.length) {
    const [l, c] = fila.shift();
    if (l === fim[0] && c === fim[1]) return dist.get(`${l},${c}`);
    for (const [dl, dc] of [[0, 1], [1, 0], [0, -1], [-1, 0]]) {
      const a = l + dl;
      const b = c + dc;
      if (grade[a]?.[b] === 0 && !dist.has(`${a},${b}`)) {
        dist.set(`${a},${b}`, dist.get(`${l},${c}`) + 1);
        fila.push([a, b]);
      }
    }
  }
  return null;
}

test('linha reta sem obstáculos', () => {
  const { grade, inicio, fim } = lerMapa(['S...G']);
  const r = aEstrela(grade, inicio, fim);
  assert.equal(r.custo, 4);
  assert.deepEqual(r.caminho, [[0, 0], [0, 1], [0, 2], [0, 3], [0, 4]]);
});

test('contorna parede', () => {
  const { grade, inicio, fim } = lerMapa([
    'S.#..',
    '..#.G',
    '..#..',
    '.....',
  ]);
  const r = aEstrela(grade, inicio, fim);
  assert.equal(r.custo, 9); // desce 3, cruza 4 colunas, sobe 2
  assert.equal(r.caminho.length - 1, r.custo);
  assert.deepEqual(r.caminho[0], [0, 0]);
  assert.deepEqual(r.caminho.at(-1), [1, 4]);
  assert.ok(r.caminho.every(([l, c]) => grade[l][c] === 0));
});

test('sem caminho retorna null', () => {
  const { grade, inicio, fim } = lerMapa(['S#G']);
  assert.equal(aEstrela(grade, inicio, fim), null);
});

test('início/fim em parede ou fora da grade retorna null', () => {
  const grade = [[0, 1], [0, 0]];
  assert.equal(aEstrela(grade, [0, 1], [1, 1]), null);
  assert.equal(aEstrela(grade, [0, 0], [0, 1]), null);
  assert.equal(aEstrela(grade, [0, 0], [5, 5]), null);
});

test('início igual ao fim', () => {
  const r = aEstrela([[0]], [0, 0], [0, 0]);
  assert.deepEqual(r.caminho, [[0, 0]]);
  assert.equal(r.custo, 0);
});

test('diagonal encurta o caminho, mas não corta quinas', () => {
  const grade = [[0, 0, 0], [0, 0, 0], [0, 0, 0]];
  const d = aEstrela(grade, [0, 0], [2, 2], { diagonal: true });
  assert.ok(Math.abs(d.custo - 2 * Math.SQRT2) < 1e-9);
  assert.equal(d.caminho.length, 3);
  const bloqueado = [[0, 1], [0, 0]];
  const r = aEstrela(bloqueado, [0, 0], [1, 1], { diagonal: true });
  assert.equal(r.custo, 2); // diagonal direta cortaria a quina da parede
  const cego = [[0, 1], [1, 0]];
  assert.equal(aEstrela(cego, [0, 0], [1, 1], { diagonal: true }), null);
});

test('custos de terreno desviam do terreno caro', () => {
  const grade = [[0, 0, 0], [0, 0, 0]];
  const custos = [[1, 1, 1], [1, 1, 1]];
  assert.equal(aEstrela(grade, [0, 0], [0, 2], { custos }).custo, 2);
  const caro = [[1, 9, 1], [1, 1, 1]];
  const r = aEstrela(grade, [0, 0], [0, 2], { custos: caro });
  assert.equal(r.custo, 4);
  assert.deepEqual(r.caminho[1], [1, 0]);
});

test('comprimento ótimo coincide com BFS em grades aleatórias', () => {
  const rng = mulberry32(2024);
  for (let t = 0; t < 60; t++) {
    const grade = Array.from({ length: 12 }, () => Array.from({ length: 12 }, () => (rng() < 0.28 ? 1 : 0)));
    grade[0][0] = 0;
    grade[11][11] = 0;
    const esperado = bfs(grade, [0, 0], [11, 11]);
    const r = aEstrela(grade, [0, 0], [11, 11]);
    if (esperado === null) assert.equal(r, null);
    else {
      assert.equal(r.custo, esperado);
      assert.equal(r.caminho.length - 1, esperado);
      for (let i = 1; i < r.caminho.length; i++) {
        const [a, b] = r.caminho[i - 1];
        const [c, d] = r.caminho[i];
        assert.equal(Math.abs(a - c) + Math.abs(b - d), 1);
        assert.equal(grade[c][d], 0);
      }
    }
  }
});

test('heurística visita menos nós que a grade inteira em campo aberto', () => {
  const grade = Array.from({ length: 30 }, () => Array(30).fill(0));
  const r = aEstrela(grade, [0, 0], [29, 29]);
  assert.equal(r.custo, 58);
  assert.ok(r.visitados <= 900);
});
