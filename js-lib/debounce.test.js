import { test, mock } from 'node:test';
import assert from 'node:assert/strict';
import { debounce } from './debounce.js';

test('chama só uma vez com os últimos argumentos', () => {
  mock.timers.enable({ apis: ['setTimeout'] });
  const fn = mock.fn();
  const d = debounce(fn, 100);
  d(1); mock.timers.tick(50);
  d(2); mock.timers.tick(99);
  assert.equal(fn.mock.callCount(), 0);
  mock.timers.tick(1);
  assert.equal(fn.mock.callCount(), 1);
  assert.deepEqual(fn.mock.calls[0].arguments, [2]);
  mock.timers.reset();
});
test('cancel impede a chamada', () => {
  mock.timers.enable({ apis: ['setTimeout'] });
  const fn = mock.fn();
  const d = debounce(fn, 10);
  d(); d.cancel();
  mock.timers.tick(100);
  assert.equal(fn.mock.callCount(), 0);
  mock.timers.reset();
});
