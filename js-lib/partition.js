// Separa a lista em [satisfazem, nãoSatisfazem].
export function partition(lista, predicado) {
  const sim = [], nao = [];
  lista.forEach((x, i) => (predicado(x, i) ? sim : nao).push(x));
  return [sim, nao];
}
