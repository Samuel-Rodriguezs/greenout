// Maior subsequência crescente estrita (LIS) em O(n log n), com reconstrução.
export function lis(v) {
  const caudas = [];   // caudas[k] = índice do menor final de subsequência de tamanho k+1
  const pai = new Array(v.length).fill(-1);
  for (let i = 0; i < v.length; i++) {
    let lo = 0, hi = caudas.length;
    while (lo < hi) {
      const m = (lo + hi) >> 1;
      if (v[caudas[m]] < v[i]) lo = m + 1; else hi = m;
    }
    if (lo > 0) pai[i] = caudas[lo - 1];
    caudas[lo] = i;
  }
  const saida = [];
  for (let i = caudas.length ? caudas[caudas.length - 1] : -1; i !== -1; i = pai[i]) saida.push(v[i]);
  return saida.reverse();
}

export const tamanhoLis = (v) => lis(v).length;
