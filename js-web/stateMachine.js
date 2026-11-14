export function createMachine(config) {
  const { initial, states, context: initialContext = {} } = config;
  if (!states[initial]) throw new Error(`Estado inicial inexistente: ${initial}`);

  const normalize = (t) => {
    if (t == null) return [];
    const arr = Array.isArray(t) ? t : [t];
    return arr.map((x) => (typeof x === 'string' ? { target: x } : x));
  };

  function runActions(actions, ctx, event) {
    let next = ctx;
    for (const a of [].concat(actions ?? [])) {
      const res = typeof a === 'function' ? a(next, event) : undefined;
      if (res && typeof res === 'object') next = { ...next, ...res };
    }
    return next;
  }

  function transition(state, event) {
    const ev = typeof event === 'string' ? { type: event } : event;
    const node = states[state.value];
    const candidates = normalize(node.on?.[ev.type]);
    for (const t of candidates) {
      if (t.guard && !t.guard(state.context, ev)) continue;
      const target = t.target ?? state.value;
      if (!states[target]) throw new Error(`Estado desconhecido: ${target}`);
      let ctx = state.context;
      const changed = target !== state.value;
      if (changed) ctx = runActions(node.exit, ctx, ev);
      ctx = runActions(t.actions, ctx, ev);
      if (changed) ctx = runActions(states[target].entry, ctx, ev);
      return { value: target, context: ctx, changed: changed || ctx !== state.context };
    }
    return { ...state, changed: false };
  }

  const initialState = { value: initial, context: runActions(states[initial].entry, initialContext, { type: 'init' }) };

  return {
    initialState,
    transition,
    interpret() {
      let state = initialState;
      const listeners = new Set();
      const service = {
        get state() { return state; },
        send(event) {
          const next = transition(state, event);
          if (next.changed) {
            state = { value: next.value, context: next.context };
            listeners.forEach((l) => l(state));
          }
          return state;
        },
        subscribe(fn) {
          listeners.add(fn);
          return () => listeners.delete(fn);
        },
        can(event) {
          return transition(state, event).changed;
        },
        matches: (v) => state.value === v,
      };
      return service;
    },
  };
}
