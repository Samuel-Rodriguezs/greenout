let activeEffect = null;
let batchDepth = 0;
const pending = new Set();

function flush() {
  for (const fn of [...pending]) {
    pending.delete(fn);
    fn();
  }
}

export function signal(initial) {
  let value = initial;
  const subs = new Set();
  const read = () => {
    if (activeEffect) {
      subs.add(activeEffect);
      activeEffect.deps.add(subs);
    }
    return value;
  };
  read.set = (next) => {
    if (Object.is(next, value)) return;
    value = next;
    for (const s of [...subs]) pending.add(s);
    if (batchDepth === 0) flush();
  };
  read.update = (fn) => read.set(fn(value));
  read.peek = () => value;
  return read;
}

export function effect(fn) {
  let cleanup;
  const runner = () => {
    if (runner.disposed) return;
    for (const d of runner.deps) d.delete(runner);
    runner.deps.clear();
    if (typeof cleanup === 'function') cleanup();
    const prev = activeEffect;
    activeEffect = runner;
    try {
      cleanup = fn();
    } finally {
      activeEffect = prev;
    }
  };
  runner.deps = new Set();
  runner.disposed = false;
  runner();
  return () => {
    runner.disposed = true;
    for (const d of runner.deps) d.delete(runner);
    runner.deps.clear();
    if (typeof cleanup === 'function') cleanup();
  };
}

export function computed(fn) {
  const s = signal(undefined);
  effect(() => {
    s.set(fn());
  });
  const read = () => s();
  read.peek = () => s.peek();
  return read;
}

export function batch(fn) {
  batchDepth++;
  try {
    fn();
  } finally {
    batchDepth--;
    if (batchDepth === 0) flush();
  }
}
