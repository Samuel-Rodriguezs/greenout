// Busca binária e variantes sobre vetor ordenado.
const padrao = (a, b) => (a < b ? -1 : a > b ? 1 : 0);

// Primeiro índice i com v[i] >= x (v.length se nenhum).
export function limiteInferior(v, x, cmp = padrao) {
  let lo = 0, hi = v.length;
  while (lo < hi) {
    const m = (lo + hi) >>> 1;
    if (cmp(v[m], x) < 0) lo = m + 1; else hi = m;
  }
  return lo;
}

// Primeiro índice i com v[i] > x (v.length se nenhum).
export function limiteSuperior(v, x, cmp = padrao) {
  let lo = 0, hi = v.length;
  while (lo < hi) {
    const m = (lo + hi) >>> 1;
    if (cmp(v[m], x) <= 0) lo = m + 1; else hi = m;
  }
  return lo;
}

// Índice de x ou -1.
export function buscaBinaria(v, x, cmp = padrao) {
  const i = limiteInferior(v, x, cmp);
  return i < v.length && cmp(v[i], x) === 0 ? i : -1;
}

// Quantidade de ocorrências de x.
export function contar(v, x, cmp = padrao) {
  return limiteSuperior(v, x, cmp) - limiteInferior(v, x, cmp);
}

// Menor n em [lo, hi] tal que predicado(n) é verdadeiro (predicado monótono).
// Devolve hi + 1 se nunca for verdadeiro.
export function buscaNaResposta(lo, hi, predicado) {
  let a = lo, b = hi + 1;
  while (a < b) {
    const m = a + Math.floor((b - a) / 2);
    if (predicado(m)) b = m; else a = m + 1;
  }
  return a;
}
