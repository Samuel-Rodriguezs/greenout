// Ordena (sem mutar) por um ou mais critérios; prefixo "-" em string indica ordem decrescente.
export function sortBy(lista, ...criterios) {
  const fns = criterios.map((c) => {
    if (typeof c === 'function') return [c, 1];
    const desc = c.startsWith('-');
    const nome = desc ? c.slice(1) : c;
    return [(o) => o[nome], desc ? -1 : 1];
  });
  return [...lista].sort((a, b) => {
    for (const [fn, dir] of fns) {
      const va = fn(a), vb = fn(b);
      if (va < vb) return -1 * dir;
      if (va > vb) return 1 * dir;
    }
    return 0;
  });
}
