import { test } from 'node:test';
import assert from 'node:assert/strict';
import { mulberry32, inteiroEntre, embaralhar } from './aleatorio.js';

test('mesma seed gera mesma sequência', () => {
  const a = mulberry32(42), b = mulberry32(42);
  const sa = Array.from({ length: 5 }, a), sb = Array.from({ length: 5 }, b);
  assert.deepEqual(sa, sb);
});
test('seeds diferentes divergem e valores em [0,1)', () => {
  const a = mulberry32(1), b = mulberry32(2);
  assert.notEqual(a(), b());
  const r = mulberry32(7);
  for (let i = 0; i < 1000; i++) { const v = r(); assert.ok(v >= 0 && v < 1); }
});
test('inteiroEntre cobre limites', () => {
  const r = mulberry32(3);
  const vistos = new Set(Array.from({ length: 500 }, () => inteiroEntre(r, 1, 3)));
  assert.deepEqual([...vistos].sort(), [1, 2, 3]);
});
test('embaralhar é permutação determinística', () => {
  const l = [1, 2, 3, 4, 5, 6];
  const x = embaralhar(l, mulberry32(9)), y = embaralhar(l, mulberry32(9));
  assert.deepEqual(x, y);
  assert.deepEqual([...x].sort(), l);
  assert.deepEqual(l, [1, 2, 3, 4, 5, 6]);
});
