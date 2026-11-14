// Fila de mutações com persistência injetável e sincronização com retry/backoff.
export function createOfflineQueue({
  send,
  storage = new Map(),
  storageKey = 'fila',
  maxTentativas = 3,
  online = true,
  gerarId = () => `${Date.now()}-${Math.random().toString(36).slice(2, 8)}`,
} = {}) {
  let isOnline = online;
  let syncing = null;
  const listeners = new Set();

  const load = () => {
    const raw = storage.get(storageKey);
    return raw ? JSON.parse(raw) : [];
  };
  const save = (items) => storage.set(storageKey, JSON.stringify(items));
  const emit = (e) => listeners.forEach((l) => l(e));

  async function sync() {
    if (syncing) return syncing;
    syncing = (async () => {
      const result = { enviados: 0, descartados: 0, pendentes: 0 };
      let items = load();
      while (isOnline && items.length) {
        const item = items[0];
        try {
          await send(item.payload, item);
          items = items.slice(1);
          result.enviados++;
          save(items);
          emit({ type: 'sent', item });
        } catch (err) {
          if (err?.permanent || item.tentativas + 1 >= maxTentativas) {
            items = items.slice(1);
            result.descartados++;
            save(items);
            emit({ type: 'dropped', item, error: err });
            continue;
          }
          items = [{ ...item, tentativas: item.tentativas + 1 }, ...items.slice(1)];
          save(items);
          emit({ type: 'retry', item, error: err });
          break; // preserva a ordem: tenta de novo na próxima sincronização
        }
      }
      result.pendentes = items.length;
      return result;
    })().finally(() => { syncing = null; });
    return syncing;
  }

  return {
    async enqueue(payload) {
      const item = { id: gerarId(), payload, tentativas: 0 };
      save([...load(), item]);
      emit({ type: 'queued', item });
      if (isOnline) await sync();
      return item.id;
    },
    sync,
    setOnline(v) {
      const mudou = v !== isOnline;
      isOnline = v;
      return mudou && v ? sync() : Promise.resolve(null);
    },
    get online() { return isOnline; },
    get pendentes() { return load().length; },
    list: load,
    subscribe(fn) { listeners.add(fn); return () => listeners.delete(fn); },
  };
}
