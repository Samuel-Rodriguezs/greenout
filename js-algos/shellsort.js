// Shell sort com a sequência de Ciura (estendida por 2.25).
const CIURA = [1, 4, 10, 23, 57, 132, 301, 701];

function lacunas(n) {
  const g = [...CIURA];
  while (g[g.length - 1] * 2.25 < n) g.push(Math.floor(g[g.length - 1] * 2.25));
  return g.filter((x) => x < n).reverse();
}

export function shellsort(arr, cmp = (a, b) => a - b) {
  const v = [...arr];
  for (const h of lacunas(v.length)) {
    for (let i = h; i < v.length; i++) {
      const tmp = v[i];
      let j = i;
      while (j >= h && cmp(v[j - h], tmp) > 0) { v[j] = v[j - h]; j -= h; }
      v[j] = tmp;
    }
  }
  return v;
}
