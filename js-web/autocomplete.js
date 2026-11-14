// search(query, { signal }) => Promise<resultados>
export function createAutocomplete(search, { delay = 300, minChars = 2, onChange = () => {} } = {}) {
  let timer = null;
  let controller = null;
  let seq = 0;
  let state = { query: '', status: 'idle', results: [], error: null };

  const set = (patch) => {
    state = { ...state, ...patch };
    onChange(state);
  };

  function cancelPending() {
    clearTimeout(timer);
    timer = null;
    if (controller) {
      controller.abort();
      controller = null;
    }
  }

  async function run(query) {
    const id = ++seq;
    controller = new AbortController();
    const { signal } = controller;
    set({ status: 'loading', error: null });
    try {
      const results = await search(query, { signal });
      if (id !== seq || signal.aborted) return;
      set({ status: 'done', results });
    } catch (error) {
      if (id !== seq || signal.aborted) return;
      set({ status: 'error', error });
    } finally {
      if (id === seq) controller = null;
    }
  }

  return {
    get state() { return state; },
    input(query) {
      cancelPending();
      seq++;
      state = { ...state, query };
      if (query.trim().length < minChars) {
        set({ status: 'idle', results: [], error: null });
        return;
      }
      timer = setTimeout(() => {
        timer = null;
        run(query.trim());
      }, delay);
    },
    cancel() {
      cancelPending();
      seq++;
      set({ status: 'idle' });
    },
  };
}
