const ehObjetoPuro = (v) => v !== null && typeof v === 'object' && Object.getPrototypeOf(v) === Object.prototype;

// Mescla objetos recursivamente (sem mutar). Arrays são substituídos.
export function mergeDeep(...fontes) {
  const saida = {};
  for (const fonte of fontes) {
    for (const [k, v] of Object.entries(fonte ?? {})) {
      if (k === '__proto__' || k === 'constructor') continue;
      if (ehObjetoPuro(v) && ehObjetoPuro(saida[k])) saida[k] = mergeDeep(saida[k], v);
      else if (ehObjetoPuro(v)) saida[k] = mergeDeep(v);
      else saida[k] = Array.isArray(v) ? [...v] : v;
    }
  }
  return saida;
}
