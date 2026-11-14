import test from 'node:test';
import assert from 'node:assert/strict';
import { criarBola, passo, simular, energia, emRepouso } from './bolaQuicando.js';

test('queda livre acelera conforme a gravidade', () => {
  const b = passo(criarBola({ y: 10 }), 0.1, { gravidade: 10 });
  assert.ok(Math.abs(b.vy - 1) < 1e-9);
  assert.ok(Math.abs(b.y - 10.1) < 1e-9);
});

test('sem gravidade, movimento retilíneo uniforme', () => {
  const b = simular(criarBola({ x: 10, y: 50, vx: 2, vy: -1 }), 0.5, 4, { gravidade: 0 });
  assert.ok(Math.abs(b.x - 14) < 1e-9);
  assert.ok(Math.abs(b.y - 48) < 1e-9);
});

test('quica no chão invertendo e reduzindo a velocidade vertical', () => {
  const b = passo(criarBola({ y: 98.5, vy: 10, raio: 1, restituicao: 0.5 }), 0.1);
  assert.equal(b.y, 99);
  assert.ok(b.vy < 0);
  assert.ok(Math.abs(b.vy) < 0.5 * 11 + 1e-9);
});

test('quica nas paredes e no teto', () => {
  const e = passo(criarBola({ x: 1.2, y: 50, vx: -5, raio: 1, restituicao: 1 }), 0.1, { gravidade: 0 });
  assert.ok(e.vx > 0 && e.x >= 1);
  const d = passo(criarBola({ x: 98.8, y: 50, vx: 5, raio: 1, restituicao: 1 }), 0.1, { gravidade: 0 });
  assert.ok(d.vx < 0 && d.x <= 99);
  const t = passo(criarBola({ x: 50, y: 1.2, vy: -5, raio: 1, restituicao: 1 }), 0.1, { gravidade: 0 });
  assert.ok(t.vy > 0);
});

test('a bola nunca sai da caixa', () => {
  let b = criarBola({ x: 30, y: 10, vx: 17, vy: -9, raio: 2, restituicao: 0.9 });
  for (let i = 0; i < 5000; i++) {
    b = passo(b, 0.02);
    assert.ok(b.x >= 2 && b.x <= 98 && b.y >= 2 && b.y <= 98);
  }
});

test('energia não aumenta com restituição < 1 e a bola para', () => {
  let b = criarBola({ x: 50, y: 10, vx: 0, vy: 0, raio: 1, restituicao: 0.6 });
  const e0 = energia(b);
  b = simular(b, 0.01, 6000);
  assert.ok(energia(b) < e0);
  assert.ok(emRepouso(b));
});

test('altura do segundo quique é menor que a do primeiro', () => {
  let b = criarBola({ x: 50, y: 20, raio: 1, restituicao: 0.7 });
  const picos = [];
  let subindo = false;
  let ultimoY = b.y;
  for (let i = 0; i < 4000 && picos.length < 2; i++) {
    b = passo(b, 0.005);
    if (b.vy < 0) subindo = true;
    if (subindo && b.vy >= 0) { picos.push(ultimoY); subindo = false; }
    ultimoY = b.y;
  }
  assert.equal(picos.length, 2);
  assert.ok(picos[1] > picos[0]); // y menor = mais alto
});

test('restituição 1 sem atrito conserva energia aproximadamente', () => {
  const b0 = criarBola({ x: 50, y: 20, raio: 1, restituicao: 1 });
  const b = simular(b0, 0.001, 3000);
  assert.ok(Math.abs(energia(b) - energia(b0)) / Math.abs(energia(b0)) < 0.05);
});
