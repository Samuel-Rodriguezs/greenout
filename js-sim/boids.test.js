import test from 'node:test';
import assert from 'node:assert/strict';
import { mulberry32, criarBando, passo, simular, ordemDeAlinhamento, limitarVelocidade } from './boids.js';

test('criarBando é determinístico por seed', () => {
  assert.deepEqual(criarBando(5, mulberry32(1)), criarBando(5, mulberry32(1)));
  assert.notDeepEqual(criarBando(5, mulberry32(1)), criarBando(5, mulberry32(2)));
});

test('boid solitário segue em linha reta com velocidade constante', () => {
  const b = [{ x: 10, y: 10, vx: 1, vy: 0.5 }];
  const r = passo(b);
  assert.deepEqual(r[0], { x: 11, y: 10.5, vx: 1, vy: 0.5 });
});

test('passo não muta o bando original', () => {
  const b = criarBando(10, mulberry32(3));
  const copia = JSON.parse(JSON.stringify(b));
  passo(b);
  assert.deepEqual(b, copia);
});

test('mundo toroidal: posição permanece nos limites', () => {
  let b = [{ x: 99.5, y: 0.2, vx: 1.2, vy: -1.2 }];
  b = passo(b);
  assert.ok(b[0].x >= 0 && b[0].x < 100);
  assert.ok(b[0].y >= 0 && b[0].y < 100);
  assert.ok(Math.abs(b[0].x - 0.7) < 1e-9);
  assert.ok(Math.abs(b[0].y - 99) < 1e-9);
});

test('limite de velocidade', () => {
  const b = limitarVelocidade({ vx: 30, vy: 40 }, 5);
  assert.ok(Math.abs(Math.hypot(b.vx, b.vy) - 5) < 1e-9);
  let bando = criarBando(30, mulberry32(4));
  bando = simular(bando, 50);
  assert.ok(bando.every((x) => Math.hypot(x.vx, x.vy) <= 2 + 1e-9));
});

test('coesão aproxima dois boids parados', () => {
  const b = [{ x: 40, y: 50, vx: 0, vy: 0 }, { x: 55, y: 50, vx: 0, vy: 0 }];
  const r = passo(b, { pesoCoesao: 0.1 });
  assert.ok(r[1].x - r[0].x < 15);
  assert.ok(r[0].vx > 0 && r[1].vx < 0);
});

test('separação afasta boids muito próximos', () => {
  const b = [{ x: 50, y: 50, vx: 0, vy: 0 }, { x: 52, y: 50, vx: 0, vy: 0 }];
  const r = passo(b, { pesoCoesao: 0, pesoAlinhamento: 0 });
  assert.ok(r[0].vx < 0 && r[1].vx > 0);
});

test('alinhamento aumenta a ordem do bando', () => {
  const inicio = criarBando(40, mulberry32(10), 50, 50);
  const params = { largura: 50, altura: 50, pesoAlinhamento: 0.2, pesoCoesao: 0, pesoSeparacao: 0, raioVisao: 50 };
  const fim = simular(inicio, 100, params);
  assert.ok(ordemDeAlinhamento(fim) > ordemDeAlinhamento(inicio));
  assert.ok(ordemDeAlinhamento(fim) > 0.9);
});

test('simulação completa é reprodutível', () => {
  const a = simular(criarBando(20, mulberry32(8)), 30);
  const b = simular(criarBando(20, mulberry32(8)), 30);
  assert.deepEqual(a, b);
});
