// Agrupa itens por chave (função ou nome de propriedade).

export function groupBy(itens, chave) {
  const obterChave = typeof chave === 'function' ? chave : (item) => item[chave];
  const grupos = {};
  let indice = 0;
  for (const item of itens) {
    const k = obterChave(item, indice++);
    if (!Object.prototype.hasOwnProperty.call(grupos, k)) grupos[k] = [];
    grupos[k].push(item);
  }
  return grupos;
}

/** Conta ocorrências por chave. */
export function contarPor(itens, chave) {
  const grupos = groupBy(itens, chave);
  return Object.fromEntries(Object.entries(grupos).map(([k, v]) => [k, v.length]));
}
