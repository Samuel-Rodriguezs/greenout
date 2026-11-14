function compile(pattern) {
  const keys = [];
  const src = pattern
    .replace(/^\/+|\/+$/g, '')
    .split('/')
    .map((seg) => {
      if (seg.startsWith(':')) {
        keys.push(seg.slice(1));
        return '([^/]+)';
      }
      if (seg === '*') {
        keys.push('*');
        return '(.*)';
      }
      return seg.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
    })
    .join('/');
  return { re: new RegExp(`^${src}$`), keys };
}

export function parseHash(hash) {
  let h = String(hash ?? '').replace(/^#/, '');
  const qi = h.indexOf('?');
  let query = {};
  if (qi >= 0) {
    query = Object.fromEntries(new URLSearchParams(h.slice(qi + 1)));
    h = h.slice(0, qi);
  }
  return { path: h.replace(/^\/+|\/+$/g, ''), query };
}

export function createRouter(routes, { notFound = null } = {}) {
  const compiled = routes.map((r) => ({ ...r, ...compile(r.path) }));
  return {
    match(hash) {
      const { path, query } = parseHash(hash);
      for (const r of compiled) {
        const m = r.re.exec(path);
        if (m) {
          const params = {};
          r.keys.forEach((k, i) => { params[k] = decodeURIComponent(m[i + 1]); });
          return { route: r.name ?? r.path, handler: r.handler, params, query };
        }
      }
      return notFound ? { route: null, handler: notFound, params: {}, query } : null;
    },
    resolve(hash) {
      const m = this.match(hash);
      return m ? m.handler?.(m) : undefined;
    },
    href(name, params = {}) {
      const r = compiled.find((c) => (c.name ?? c.path) === name);
      if (!r) throw new Error(`Rota desconhecida: ${name}`);
      const path = r.path.replace(/:([A-Za-z0-9_]+)/g, (_, k) => {
        if (!(k in params)) throw new Error(`Parâmetro ausente: ${k}`);
        return encodeURIComponent(params[k]);
      });
      return `#/${path.replace(/^\/+/, '')}`;
    },
  };
}
