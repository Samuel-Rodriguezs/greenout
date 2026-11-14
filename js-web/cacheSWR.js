// Cache stale-while-revalidate. fetcher(key) => Promise<valor>. `agora` injetável para testes.
export function createSWRCache(fetcher, { ttl = 60_000, staleTtl = 600_000, agora = () => Date.now() } = {}) {
  const store = new Map(); // key -> { value, at }
  const inflight = new Map(); // key -> Promise

  function revalidate(key) {
    if (inflight.has(key)) return inflight.get(key);
    const p = Promise.resolve()
      .then(() => fetcher(key))
      .then((value) => {
        store.set(key, { value, at: agora() });
        return value;
      })
      .finally(() => inflight.delete(key));
    inflight.set(key, p);
    return p;
  }

  return {
    // Retorna { value, status: 'fresh'|'stale'|'miss', revalidating?: Promise }
    async get(key) {
      const e = store.get(key);
      if (e) {
        const idade = agora() - e.at;
        if (idade < ttl) return { value: e.value, status: 'fresh' };
        if (idade < ttl + staleTtl) {
          const revalidating = revalidate(key);
          revalidating.catch(() => {});
          return { value: e.value, status: 'stale', revalidating };
        }
        store.delete(key);
      }
      return { value: await revalidate(key), status: 'miss' };
    },
    peek: (key) => store.get(key)?.value,
    set(key, value) { store.set(key, { value, at: agora() }); },
    invalidate(key) { store.delete(key); },
    clear() { store.clear(); },
    get size() { return store.size; },
  };
}
