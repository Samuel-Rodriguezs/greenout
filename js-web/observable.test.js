import test, { mock } from 'node:test';
import assert from 'node:assert/strict';
import { Observable, of, map, filter, take, debounce, Subject } from './observable.js';

test('of + map + filter', () => {
  const out = [];
  of(1, 2, 3, 4).pipe(map((x) => x * 2), filter((x) => x > 2)).subscribe((v) => out.push(v));
  assert.deepEqual(out, [4, 6, 8]);
});

test('complete é propagado', () => {
  let done = false;
  of(1).pipe(map((x) => x)).subscribe({ next() {}, complete: () => { done = true; } });
  assert.equal(done, true);
});

test('take completa e faz teardown', () => {
  const s = new Subject();
  const out = [];
  let done = false;
  s.pipe(take(2)).subscribe({ next: (v) => out.push(v), complete: () => { done = true; } });
  s.next(1); s.next(2); s.next(3);
  assert.deepEqual(out, [1, 2]);
  assert.equal(done, true);
  assert.equal(s._observers.size, 0);
});

test('unsubscribe executa teardown', () => {
  let torn = false;
  const o = new Observable(() => () => { torn = true; });
  const sub = o.subscribe(() => {});
  sub.unsubscribe();
  assert.equal(torn, true);
});

test('debounce emite só o último valor', (t) => {
  t.mock.timers.enable({ apis: ['setTimeout'] });
  const s = new Subject();
  const out = [];
  s.pipe(debounce(100)).subscribe((v) => out.push(v));
  s.next('a');
  t.mock.timers.tick(50);
  s.next('b');
  t.mock.timers.tick(99);
  assert.deepEqual(out, []);
  t.mock.timers.tick(1);
  assert.deepEqual(out, ['b']);
});

test('debounce emite pendente ao completar', (t) => {
  t.mock.timers.enable({ apis: ['setTimeout'] });
  const s = new Subject();
  const out = [];
  s.pipe(debounce(100)).subscribe({ next: (v) => out.push(v), complete: () => out.push('fim') });
  s.next(1);
  s.complete();
  assert.deepEqual(out, [1, 'fim']);
});

test('erro encerra a inscrição', () => {
  const errs = [];
  const o = new Observable((ob) => { ob.error(new Error('x')); ob.next(1); });
  const vals = [];
  o.subscribe({ next: (v) => vals.push(v), error: (e) => errs.push(e.message) });
  assert.deepEqual(errs, ['x']);
  assert.deepEqual(vals, []);
});
