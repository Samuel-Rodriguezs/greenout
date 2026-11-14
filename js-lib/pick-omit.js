// Cria objeto só com as chaves indicadas (que existam).
export function pick(obj, chaves) {
  const r = {};
  for (const k of chaves) if (Object.hasOwn(obj, k)) r[k] = obj[k];
  return r;
}
// Cria objeto sem as chaves indicadas.
export function omit(obj, chaves) {
  const fora = new Set(chaves);
  return Object.fromEntries(Object.entries(obj).filter(([k]) => !fora.has(k)));
}
