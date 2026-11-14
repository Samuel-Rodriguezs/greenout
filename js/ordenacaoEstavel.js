// Merge sort estável, sem mutar a entrada.

const comparadorPadrao = (a, b) => (a < b ? -1 : a > b ? 1 : 0);

export function ordenarEstavel(array, comparar = comparadorPadrao) {
  if (array.length <= 1) return [...array];
  const meio = Math.floor(array.length / 2);
  const esquerda = ordenarEstavel(array.slice(0, meio), comparar);
  const direita = ordenarEstavel(array.slice(meio), comparar);

  const saida = [];
  let i = 0;
  let j = 0;
  while (i < esquerda.length && j < direita.length) {
    // `<= 0` favorece a esquerda em empates, o que garante a estabilidade.
    if (comparar(esquerda[i], direita[j]) <= 0) saida.push(esquerda[i++]);
    else saida.push(direita[j++]);
  }
  while (i < esquerda.length) saida.push(esquerda[i++]);
  while (j < direita.length) saida.push(direita[j++]);
  return saida;
}

/** Ordena por uma ou mais chaves (strings de propriedade); prefixo "-" indica ordem decrescente. */
export function ordenarPor(array, ...chaves) {
  const comparar = (a, b) => {
    for (const chave of chaves) {
      const desc = chave.startsWith('-');
      const nome = desc ? chave.slice(1) : chave;
      const r = comparadorPadrao(a[nome], b[nome]);
      if (r !== 0) return desc ? -r : r;
    }
    return 0;
  };
  return ordenarEstavel(array, comparar);
}
