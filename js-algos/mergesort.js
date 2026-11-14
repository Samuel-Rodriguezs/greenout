// Merge sort estável, top-down com buffer auxiliar único.
export function mergesort(arr, cmp = (a, b) => a - b) {
  const v = [...arr];
  const aux = new Array(v.length);
  const ordenar = (lo, hi) => { // [lo, hi)
    if (hi - lo < 2) return;
    const meio = (lo + hi) >> 1;
    ordenar(lo, meio);
    ordenar(meio, hi);
    let i = lo, j = meio, k = lo;
    while (i < meio && j < hi) aux[k++] = cmp(v[j], v[i]) < 0 ? v[j++] : v[i++];
    while (i < meio) aux[k++] = v[i++];
    while (j < hi) aux[k++] = v[j++];
    for (k = lo; k < hi; k++) v[k] = aux[k];
  };
  ordenar(0, v.length);
  return v;
}
