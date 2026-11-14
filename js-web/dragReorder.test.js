import test from 'node:test';
import assert from 'node:assert/strict';
import { moveItem, dropIndex, reorderByIds, moveMany, positionBetween, previewOrder } from './dragReorder.js';

test('moveItem para frente e para trás sem mutar', () => {
  const l = ['a', 'b', 'c', 'd'];
  assert.deepEqual(moveItem(l, 0, 2), ['b', 'c', 'a', 'd']);
  assert.deepEqual(moveItem(l, 3, 0), ['d', 'a', 'b', 'c']);
  assert.deepEqual(moveItem(l, 1, 99), ['a', 'c', 'd', 'b']);
  assert.deepEqual(l, ['a', 'b', 'c', 'd']);
  assert.throws(() => moveItem(l, 9, 0), RangeError);
});

test('dropIndex usa ponto médio', () => {
  const h = [40, 40, 40];
  assert.equal(dropIndex(10, h), 0);
  assert.equal(dropIndex(25, h), 1);
  assert.equal(dropIndex(70, h), 2);
  assert.equal(dropIndex(500, h), 2);
  assert.equal(dropIndex(110, h, { originTop: 100 }), 0);
});

test('reorderByIds', () => {
  const items = [{ id: 1 }, { id: 2 }, { id: 3 }];
  assert.deepEqual(reorderByIds(items, [3, 1]).map((i) => i.id), [3, 1, 2]);
  assert.deepEqual(reorderByIds(items, [9, 2]).map((i) => i.id), [2, 1, 3]);
});

test('moveMany preserva ordem relativa', () => {
  const l = ['a', 'b', 'c', 'd', 'e'];
  assert.deepEqual(moveMany(l, [0, 2], 4), ['b', 'd', 'a', 'c', 'e']);
  assert.deepEqual(moveMany(l, [3, 4], 0), ['d', 'e', 'a', 'b', 'c']);
  assert.deepEqual(moveMany(l, [1], 1), l);
});

test('positionBetween', () => {
  assert.equal(positionBetween(null, null), 1);
  assert.equal(positionBetween(null, 4), 2);
  assert.equal(positionBetween(4, null), 5);
  assert.equal(positionBetween(1, 2), 1.5);
});

test('previewOrder marca o item movido', () => {
  const p = previewOrder(['a', 'b', 'c'], 0, 2);
  assert.deepEqual(p.map((x) => x.item), ['b', 'c', 'a']);
  assert.deepEqual(p.filter((x) => x.moved).map((x) => x.index), [2]);
});
