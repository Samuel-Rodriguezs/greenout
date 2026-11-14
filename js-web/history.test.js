import test from 'node:test';
import assert from 'node:assert/strict';
import { createHistory } from './history.js';

test('push, undo e redo', () => {
  const h = createHistory('a');
  h.push('b');
  h.push('c');
  assert.equal(h.state, 'c');
  assert.equal(h.undo(), 'b');
  assert.equal(h.undo(), 'a');
  assert.equal(h.canUndo, false);
  assert.equal(h.undo(), 'a');
  assert.equal(h.redo(), 'b');
  assert.equal(h.redo(), 'c');
  assert.equal(h.canRedo, false);
});

test('novo push descarta o futuro', () => {
  const h = createHistory(1);
  h.push(2);
  h.push(3);
  h.undo();
  h.push(9);
  assert.equal(h.canRedo, false);
  assert.equal(h.undo(), 2);
});

test('limite descarta o mais antigo', () => {
  const h = createHistory(0, { limit: 2 });
  [1, 2, 3].forEach((v) => h.push(v));
  assert.deepEqual(h.size, { past: 2, future: 0 });
  h.undo();
  h.undo();
  assert.equal(h.state, 1);
});

test('valor igual não cria entrada', () => {
  const h = createHistory('x');
  h.push('x');
  assert.equal(h.canUndo, false);
});

test('clear mantém o presente', () => {
  const h = createHistory(1);
  h.push(2);
  h.undo();
  h.clear();
  assert.equal(h.state, 1);
  assert.equal(h.canRedo, false);
  assert.equal(h.canUndo, false);
});
