import test from 'node:test';
import assert from 'node:assert/strict';
import { visibleWindow, createVariableWindow, scrollToIndex } from './virtualList.js';

test('janela no topo', () => {
  const w = visibleWindow({ scrollTop: 0, viewportHeight: 100, itemHeight: 20, total: 1000, overscan: 2 });
  assert.deepEqual(w, { start: 0, end: 7, offsetTop: 0, totalHeight: 20000, items: 7 });
});

test('janela no meio com overscan', () => {
  const w = visibleWindow({ scrollTop: 1000, viewportHeight: 100, itemHeight: 20, total: 1000, overscan: 3 });
  assert.equal(w.start, 47);
  assert.equal(w.end, 58);
  assert.equal(w.offsetTop, 940);
});

test('janela no fim e scroll excessivo', () => {
  const w = visibleWindow({ scrollTop: 99999, viewportHeight: 100, itemHeight: 20, total: 50, overscan: 1 });
  assert.equal(w.end, 50);
  assert.equal(w.start, 44);
});

test('lista vazia e itemHeight inválido', () => {
  assert.equal(visibleWindow({ scrollTop: 0, viewportHeight: 100, itemHeight: 10, total: 0 }).items, 0);
  assert.throws(() => visibleWindow({ scrollTop: 0, viewportHeight: 1, itemHeight: 0, total: 1 }));
});

test('alturas variáveis', () => {
  const vw = createVariableWindow([10, 20, 30, 40, 50]);
  assert.equal(vw.totalHeight, 150);
  assert.equal(vw.offsetOf(3), 60);
  const r = vw.range({ scrollTop: 35, viewportHeight: 30, overscan: 0 });
  assert.deepEqual([r.start, r.end, r.offsetTop], [2, 4, 30]);
  const r2 = vw.range({ scrollTop: 35, viewportHeight: 30 });
  assert.deepEqual([r2.start, r2.end], [0, 5]);
});

test('scrollToIndex', () => {
  const o = { itemHeight: 20, viewportHeight: 100, total: 100 };
  assert.equal(scrollToIndex(10, o), 200);
  assert.equal(scrollToIndex(10, { ...o, align: 'center' }), 160);
  assert.equal(scrollToIndex(10, { ...o, align: 'end' }), 120);
  assert.equal(scrollToIndex(999, o), 1900);
  assert.equal(scrollToIndex(0, { ...o, align: 'center' }), 0);
});
