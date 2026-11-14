import test from 'node:test';
import assert from 'node:assert/strict';
import { Vec2, Vec3 } from './vetores.js';

const perto = (a, b, eps = 1e-9) => assert.ok(Math.abs(a - b) <= eps, `${a} != ${b}`);

test('Vec2 é imutável e operações não alteram o original', () => {
  const a = new Vec2(1, 2);
  const b = a.soma(new Vec2(3, 4));
  assert.deepEqual(b.toArray(), [4, 6]);
  assert.deepEqual(a.toArray(), [1, 2]);
  assert.throws(() => { 'use strict'; a.x = 9; }, TypeError);
});

test('Vec2 norma, dot, cruz e perpendicular', () => {
  const a = new Vec2(3, 4);
  assert.equal(a.norma, 5);
  assert.equal(a.dot(new Vec2(1, 0)), 3);
  assert.equal(new Vec2(1, 0).cruz(new Vec2(0, 1)), 1);
  const p = new Vec2(1, 0).perpendicular();
  assert.equal(p.x + 0, 0);
  assert.equal(p.y, 1);
});

test('Vec2 rotação, ângulo e projeção', () => {
  const r = new Vec2(1, 0).rotaciona(Math.PI / 2);
  perto(r.x, 0);
  perto(r.y, 1);
  perto(new Vec2(0, 2).angulo(), Math.PI / 2);
  assert.deepEqual(new Vec2(3, 4).projetaEm(new Vec2(2, 0)).toArray(), [3, 0]);
});

test('Vec2 normalização e vetor nulo', () => {
  assert.equal(new Vec2(0, 10).normalizado().y, 1);
  assert.throws(() => new Vec2(0, 0).normalizado(), RangeError);
  assert.throws(() => new Vec2(1, 1).projetaEm(new Vec2(0, 0)), RangeError);
});

test('Vec2 lerp e distância', () => {
  assert.deepEqual(new Vec2(0, 0).lerp(new Vec2(10, 20), 0.5).toArray(), [5, 10]);
  assert.equal(new Vec2(0, 0).distancia(new Vec2(6, 8)), 10);
});

test('Vec3 cruz segue a regra da mão direita', () => {
  const c = new Vec3(1, 0, 0).cruz(new Vec3(0, 1, 0));
  assert.deepEqual(c.toArray(), [0, 0, 1]);
  assert.equal(new Vec3(1, 2, 3).dot(new Vec3(4, 5, 6)), 32);
});

test('Vec3 rotação em torno do eixo z', () => {
  const r = new Vec3(1, 0, 0).rotaciona(new Vec3(0, 0, 5), Math.PI / 2);
  assert.ok(r.igual(new Vec3(0, 1, 0), 1e-12));
});

test('Vec3 norma, normalização e imutabilidade', () => {
  const v = new Vec3(2, 3, 6);
  assert.equal(v.norma, 7);
  perto(v.normalizado().norma, 1);
  assert.throws(() => new Vec3().normalizado(), RangeError);
  assert.ok(Object.isFrozen(v));
});
