// Quicksort in-place com pivô mediana-de-três e partição de Hoare.
export function quicksort(arr, cmp = (a, b) => a - b) {
  const v = [...arr];
  const ordenar = (lo, hi) => {
    while (lo < hi) {
      const meio = (lo + hi) >> 1;
      // mediana de três
      if (cmp(v[meio], v[lo]) < 0) [v[meio], v[lo]] = [v[lo], v[meio]];
      if (cmp(v[hi], v[lo]) < 0) [v[hi], v[lo]] = [v[lo], v[hi]];
      if (cmp(v[hi], v[meio]) < 0) [v[hi], v[meio]] = [v[meio], v[hi]];
      const pivo = v[meio];
      let i = lo, j = hi;
      while (i <= j) {
        while (cmp(v[i], pivo) < 0) i++;
        while (cmp(v[j], pivo) > 0) j--;
        if (i <= j) { [v[i], v[j]] = [v[j], v[i]]; i++; j--; }
      }
      // recursão no lado menor, laço no maior (pilha O(log n))
      if (j - lo < hi - i) { ordenar(lo, j); lo = i; }
      else { ordenar(i, hi); hi = j; }
    }
  };
  ordenar(0, v.length - 1);
  return v;
}
