// Achata arrays aninhados até uma profundidade (padrão: 1, como Array.prototype.flat).

export function flatten(array, profundidade = 1) {
  if (!Array.isArray(array)) throw new TypeError('esperado um array');
  const saida = [];
  const visitar = (lista, nivel) => {
    for (const item of lista) {
      if (Array.isArray(item) && nivel > 0) visitar(item, nivel - 1);
      else saida.push(item);
    }
  };
  visitar(array, profundidade);
  return saida;
}

/** Achata todos os níveis, sem recursão (pilha explícita) para suportar aninhamento enorme. */
export function flattenTotal(array) {
  if (!Array.isArray(array)) throw new TypeError('esperado um array');
  const pilha = [...array];
  const saida = [];
  while (pilha.length > 0) {
    const item = pilha.pop();
    if (Array.isArray(item)) pilha.push(...item);
    else saida.push(item);
  }
  return saida.reverse();
}
