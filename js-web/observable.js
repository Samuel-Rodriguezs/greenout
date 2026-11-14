export class Observable {
  constructor(subscribeFn) {
    this._subscribeFn = subscribeFn;
  }

  subscribe(observer) {
    const obs = typeof observer === 'function' ? { next: observer } : observer;
    let closed = false;
    let teardown;
    const safe = {
      next: (v) => { if (!closed) obs.next?.(v); },
      error: (e) => {
        if (closed) return;
        closed = true;
        obs.error?.(e);
        teardown?.();
      },
      complete: () => {
        if (closed) return;
        closed = true;
        obs.complete?.();
        teardown?.();
      },
    };
    teardown = this._subscribeFn(safe);
    if (closed && typeof teardown === 'function') teardown();
    return {
      unsubscribe() {
        if (closed) return;
        closed = true;
        if (typeof teardown === 'function') teardown();
      },
    };
  }

  pipe(...ops) {
    return ops.reduce((src, op) => op(src), this);
  }
}

export const of = (...values) =>
  new Observable((o) => {
    values.forEach((v) => o.next(v));
    o.complete();
  });

export const map = (fn) => (src) =>
  new Observable((o) => {
    const s = src.subscribe({
      next: (v) => o.next(fn(v)),
      error: o.error,
      complete: o.complete,
    });
    return () => s.unsubscribe();
  });

export const filter = (pred) => (src) =>
  new Observable((o) => {
    const s = src.subscribe({
      next: (v) => { if (pred(v)) o.next(v); },
      error: o.error,
      complete: o.complete,
    });
    return () => s.unsubscribe();
  });

export const take = (n) => (src) =>
  new Observable((o) => {
    let count = 0;
    if (n <= 0) { o.complete(); return undefined; }
    const s = src.subscribe({
      next: (v) => {
        count++;
        o.next(v);
        if (count >= n) o.complete();
      },
      error: o.error,
      complete: o.complete,
    });
    return () => s.unsubscribe();
  });

export const debounce = (ms) => (src) =>
  new Observable((o) => {
    let timer = null;
    let last;
    let has = false;
    const s = src.subscribe({
      next: (v) => {
        last = v;
        has = true;
        clearTimeout(timer);
        timer = setTimeout(() => {
          has = false;
          o.next(last);
        }, ms);
      },
      error: o.error,
      complete: () => {
        clearTimeout(timer);
        if (has) o.next(last);
        o.complete();
      },
    });
    return () => {
      clearTimeout(timer);
      s.unsubscribe();
    };
  });

export class Subject extends Observable {
  constructor() {
    const observers = new Set();
    super((o) => {
      observers.add(o);
      return () => observers.delete(o);
    });
    this._observers = observers;
  }
  next(v) { [...this._observers].forEach((o) => o.next(v)); }
  complete() { [...this._observers].forEach((o) => o.complete()); }
  error(e) { [...this._observers].forEach((o) => o.error(e)); }
}
