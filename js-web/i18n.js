export function createI18n({ locale = 'pt-BR', fallback = 'en', messages = {} } = {}) {
  let current = locale;
  const dict = { ...messages };

  function lookup(loc, key) {
    let node = dict[loc];
    for (const part of key.split('.')) {
      if (node == null || typeof node !== 'object') return undefined;
      node = node[part];
    }
    return node;
  }

  function resolve(key) {
    const langs = [current, current.split('-')[0], fallback];
    for (const l of langs) {
      const v = lookup(l, key);
      if (v !== undefined) return { value: v, locale: l };
    }
    return null;
  }

  function interpolate(str, params, loc) {
    return str.replace(/\{\{\s*([\w.]+)\s*\}\}/g, (m, name) => {
      const v = name.split('.').reduce((o, k) => (o == null ? undefined : o[k]), params);
      if (v === undefined) return m;
      return typeof v === 'number' ? new Intl.NumberFormat(loc).format(v) : String(v);
    });
  }

  function t(key, params = {}) {
    const r = resolve(key);
    if (!r) return key;
    let msg = r.value;
    if (msg && typeof msg === 'object' && 'count' in params) {
      const rules = new Intl.PluralRules(r.locale);
      const cat = params.count === 0 && 'zero' in msg ? 'zero' : rules.select(params.count);
      msg = msg[cat] ?? msg.other ?? key;
    }
    if (typeof msg !== 'string') return key;
    return interpolate(msg, params, r.locale);
  }

  return {
    t,
    get locale() { return current; },
    setLocale(l) { current = l; },
    addMessages(loc, msgs) {
      dict[loc] = { ...(dict[loc] ?? {}), ...msgs };
    },
    has: (key) => resolve(key) !== null,
  };
}
