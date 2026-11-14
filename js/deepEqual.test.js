import { test } from 'node:test';
import assert from 'node:assert/strict';
import { deepEqual } from './deepEqual.js';

test('primitivos', () => {
  assert.ok(deepEqual(1, 1));
  assert.ok(!deepEqual(1, '1'));
  assert.ok(deepEqual(NaN, NaN));
  assert.ok(!deepEqual(0, -0));
  assert.ok(deepEqual(null, null));
  assert.ok(!deepEqual(null, undefined));
  assert.ok(!deepEqual(null, {}));
});

test('objetos e arrays aninhados', () => {
  assert.ok(deepEqual({ a: [1, { b: 2 }] }, { a: [1, { b: 2 }] }));
  assert.ok(!deepEqual({ a: [1, { b: 2 }] }, { a: [1, { b: 3 }] }));
  assert.ok(!deepEqual({ a: 1 }, { a: 1, b: 2 }));
  assert.ok(!deepEqual({ a: undefined }, { b: undefined }));
});

test('ordem das chaves não importa, a dos arrays sim', () => {
  assert.ok(deepEqual({ a: 1, b: 2 }, { b: 2, a: 1 }));
  assert.ok(!deepEqual([1, 2], [2, 1]));
});

test('array não é igual a objeto', () => {
  assert.ok(!deepEqual([], {}));
});

test('Date, Map e Set', () => {
  assert.ok(deepEqual(new Date(5), new Date(5)));
  assert.ok(!deepEqual(new Date(5), new Date(6)));
  assert.ok(deepEqual(new Map([[1, { a: 1 }]]), new Map([[1, { a: 1 }]])));
  assert.ok(!deepEqual(new Map([[1, 1]]), new Map([[1, 2]])));
  assert.ok(deepEqual(new Set([{ x: 1 }]), new Set([{ x: 1 }])));
  assert.ok(!deepEqual(new Set([1]), new Set([1, 2])));
});

test('estruturas circulares', () => {
  const a = { n: 1 }; a.self = a;
  const b = { n: 1 }; b.self = b;
  assert.ok(deepEqual(a, b));
});
