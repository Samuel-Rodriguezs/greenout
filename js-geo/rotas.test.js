import test from 'node:test';
import assert from 'node:assert/strict';
import { GrafoViario } from './rotas.js';
import { distanciaHaversine } from './haversine.js';

function brasil() {
  const g = new GrafoViario();
  g.adicionaNo('SP', -23.5505, -46.6333)
    .adicionaNo('Campinas', -22.9099, -47.0626)
    .adicionaNo('Rio', -22.9068, -43.1729)
    .adicionaNo('SJC', -23.1896, -45.8841)
    .adicionaNo('BH', -19.9167, -43.9345)
    .adicionaNo('Curitiba', -25.4284, -49.2733)
    .adicionaNo('Ilha', 0, 0); // isolada
  g.adicionaVia('SP', 'Campinas').adicionaVia('SP', 'SJC').adicionaVia('SJC', 'Rio')
    .adicionaVia('Campinas', 'BH').adicionaVia('BH', 'Rio').adicionaVia('SP', 'Curitiba');
  return g;
}

test('Dijkstra: SP -> Rio passa por São José dos Campos', () => {
  const r = brasil().dijkstra('SP', 'Rio');
  assert.deepEqual(r.caminho, ['SP', 'SJC', 'Rio']);
  const esperado = distanciaHaversine(-23.5505, -46.6333, -23.1896, -45.8841) +
    distanciaHaversine(-23.1896, -45.8841, -22.9068, -43.1729);
  assert.ok(Math.abs(r.distancia - esperado) < 1e-6);
});

test('A* encontra o mesmo custo que Dijkstra', () => {
  const g = brasil();
  for (const [a, b] of [['SP', 'Rio'], ['Curitiba', 'BH'], ['Campinas', 'SJC']]) {
    const d = g.dijkstra(a, b), s = g.aEstrela(a, b);
    assert.ok(Math.abs(d.distancia - s.distancia) < 1e-6, `${a}->${b}`);
    assert.deepEqual(s.caminho[0], a);
    assert.deepEqual(s.caminho.at(-1), b);
  }
});

test('A* expande no máximo tantos nós quanto Dijkstra em malha grande', () => {
  const g = new GrafoViario();
  const N = 25;
  const id = (i, j) => `${i},${j}`;
  for (let i = 0; i < N; i++) for (let j = 0; j < N; j++) g.adicionaNo(id(i, j), -23 + i * 0.01, -46 + j * 0.01);
  for (let i = 0; i < N; i++) {
    for (let j = 0; j < N; j++) {
      if (i + 1 < N) g.adicionaVia(id(i, j), id(i + 1, j));
      if (j + 1 < N) g.adicionaVia(id(i, j), id(i, j + 1));
    }
  }
  const d = g.dijkstra(id(0, 0), id(N - 1, N - 1));
  const a = g.aEstrela(id(0, 0), id(N - 1, N - 1));
  assert.ok(Math.abs(d.distancia - a.distancia) < 1e-6);
  assert.ok(a.expandidos < d.expandidos, `${a.expandidos} vs ${d.expandidos}`);
  assert.equal(a.caminho.length, 2 * (N - 1) + 1);
});

test('pesos customizados: via lenta é evitada', () => {
  const g = new GrafoViario();
  g.adicionaNo('A', 0, 0).adicionaNo('B', 0, 0.01).adicionaNo('C', 0, 0.02).adicionaNo('D', 0.005, 0.01);
  const reta = distanciaHaversine(0, 0, 0, 0.02);
  g.adicionaVia('A', 'C', { peso: reta * 5 });
  g.adicionaVia('A', 'B').adicionaVia('B', 'C');
  const r = g.aEstrela('A', 'C');
  assert.deepEqual(r.caminho, ['A', 'B', 'C']);
  assert.ok(Math.abs(r.distancia - reta) < 1e-6);
});

test('mão única é respeitada', () => {
  const g = new GrafoViario();
  g.adicionaNo('A', 0, 0).adicionaNo('B', 0, 0.01);
  g.adicionaVia('A', 'B', { mao: 'unica' });
  assert.deepEqual(g.dijkstra('A', 'B').caminho, ['A', 'B']);
  assert.equal(g.dijkstra('B', 'A').distancia, Infinity);
});

test('destino inalcançável e origem = destino', () => {
  const g = brasil();
  const sem = g.aEstrela('SP', 'Ilha');
  assert.equal(sem.distancia, Infinity);
  assert.deepEqual(sem.caminho, []);
  const mesmo = g.dijkstra('SP', 'SP');
  assert.equal(mesmo.distancia, 0);
  assert.deepEqual(mesmo.caminho, ['SP']);
});

test('validações de nós e pesos', () => {
  const g = brasil();
  assert.throws(() => g.dijkstra('SP', 'Marte'), /inexistente/);
  assert.throws(() => g.aEstrela('Marte', 'SP'), /inexistente/);
  assert.throws(() => g.adicionaNo('SP', 0, 0), /duplicado/);
  assert.throws(() => g.adicionaVia('SP', 'Rio', { peso: 10 }), RangeError);
  assert.throws(() => g.adicionaVia('SP', 'X'), /inexistente/);
});
