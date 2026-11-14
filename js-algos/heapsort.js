// Heapsort in-place (max-heap) sobre cópia do vetor.
export function heapsort(arr, cmp = (a, b) => a - b) {
  const v = [...arr];
  const n = v.length;
  const descer = (i, tam) => {
    for (;;) {
      let maior = i;
      const l = 2 * i + 1, r = l + 1;
      if (l < tam && cmp(v[l], v[maior]) > 0) maior = l;
      if (r < tam && cmp(v[r], v[maior]) > 0) maior = r;
      if (maior === i) return;
      [v[i], v[maior]] = [v[maior], v[i]];
      i = maior;
    }
  };
  for (let i = (n >> 1) - 1; i >= 0; i--) descer(i, n);
  for (let fim = n - 1; fim > 0; fim--) {
    [v[0], v[fim]] = [v[fim], v[0]];
    descer(0, fim);
  }
  return v;
}
