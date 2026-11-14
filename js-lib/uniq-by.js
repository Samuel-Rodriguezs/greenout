// Remove duplicados mantendo o primeiro, comparando pela chave calculada.
export function uniqBy(lista, chave = (x) => x) {
  const fn = typeof chave === 'string' ? (o) => o[chave] : chave;
  const vistos = new Set();
  const saida = [];
  for (const item of lista) {
    const k = fn(item);
    if (!vistos.has(k)) {
      vistos.add(k);
      saida.push(item);
    }
  }
  return saida;
}
