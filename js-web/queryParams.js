function coerce(v, tipo) {
  if (tipo === 'string' || tipo === undefined) return v;
  if (tipo === 'number') {
    const n = Number(v);
    return v === '' || Number.isNaN(n) ? undefined : n;
  }
  if (tipo === 'boolean') {
    if (['true', '1', 'sim', 'on', ''].includes(v)) return true;
    if (['false', '0', 'nao', 'não', 'off'].includes(v)) return false;
    return undefined;
  }
  if (tipo === 'date') {
    const d = new Date(v);
    return Number.isNaN(d.getTime()) ? undefined : d;
  }
  if (tipo === 'json') {
    try { return JSON.parse(v); } catch { return undefined; }
  }
  throw new Error(`Tipo desconhecido: ${tipo}`);
}

// schema: { campo: 'number' | 'boolean' | ... | { tipo, array, padrao } }
export function parseQuery(url, schema = {}) {
  const qs = String(url).includes('?') ? String(url).split('?')[1].split('#')[0] : String(url).replace(/^\?/, '');
  const sp = new URLSearchParams(qs);
  const out = {};
  for (const key of new Set(sp.keys())) {
    const nome = key.replace(/\[\]$/, '');
    const spec = typeof schema[nome] === 'string' ? { tipo: schema[nome] } : (schema[nome] ?? {});
    const bruto = sp.getAll(key);
    const isArray = spec.array || key.endsWith('[]') || bruto.length > 1;
    if (isArray) {
      out[nome] = bruto.map((v) => coerce(v, spec.tipo)).filter((v) => v !== undefined);
    } else {
      const val = coerce(bruto[0], spec.tipo);
      if (val !== undefined) out[nome] = val;
    }
  }
  for (const [k, spec] of Object.entries(schema)) {
    if (!(k in out) && typeof spec === 'object' && 'padrao' in spec) out[k] = spec.padrao;
  }
  return out;
}

export function buildQuery(obj) {
  const sp = new URLSearchParams();
  for (const [k, v] of Object.entries(obj)) {
    if (v === undefined || v === null) continue;
    const add = (x) => sp.append(Array.isArray(v) ? `${k}[]` : k, x instanceof Date ? x.toISOString() : typeof x === 'object' ? JSON.stringify(x) : String(x));
    if (Array.isArray(v)) v.forEach(add);
    else add(v);
  }
  const s = sp.toString();
  return s ? `?${s}` : '';
}
