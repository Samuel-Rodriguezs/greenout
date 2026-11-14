import { test } from 'node:test';
import assert from 'node:assert/strict';
import { clamp, lerp, inverseLerp, remap } from './matematica.js';

test('clamp', () => {
  assert.equal(clamp(15, 0, 10), 10);
  assert.equal(clamp(-5, 0, 10), 0);
  assert.equal(clamp(5, 0, 10), 5);
  assert.throws(() => clamp(1, 5, 0), RangeError);
});
test('lerp', () => {
  assert.equal(lerp(0, 10, 0.25), 2.5);
  assert.equal(lerp(10, 20, 0), 10);
});
test('inverseLerp e remap', () => {
  assert.equal(inverseLerp(0, 10, 5), 0.5);
  assert.equal(inverseLerp(3, 3, 3), 0);
  assert.equal(remap(5, 0, 10, 100, 200), 150);
});
