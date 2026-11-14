export function createHistory(initial, { limit = 100 } = {}) {
  let past = [];
  let present = initial;
  let future = [];
  return {
    get state() { return present; },
    get canUndo() { return past.length > 0; },
    get canRedo() { return future.length > 0; },
    push(next) {
      if (Object.is(next, present)) return present;
      past.push(present);
      if (past.length > limit) past.shift();
      present = next;
      future = [];
      return present;
    },
    undo() {
      if (!past.length) return present;
      future.push(present);
      present = past.pop();
      return present;
    },
    redo() {
      if (!future.length) return present;
      past.push(present);
      present = future.pop();
      return present;
    },
    clear() {
      past = [];
      future = [];
    },
    get size() { return { past: past.length, future: future.length }; },
  };
}
