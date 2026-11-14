// Radix sort LSD base 10 para inteiros (aceita negativos).
function radixNaoNegativos(v) {
  if (v.length < 2) return v;
  const max = Math.max(...v);
  let atual = v;
  for (let exp = 1; Math.floor(max / exp) > 0; exp *= 10) {
    const baldes = Array.from({ length: 10 }, () => []);
    for (const x of atual) baldes[Math.floor(x / exp) % 10].push(x);
    atual = baldes.flat();
  }
  return atual;
}

export function radixsort(arr) {
  for (const x of arr) {
    if (!Number.isInteger(x)) throw new TypeError(`radixsort só aceita inteiros: ${x}`);
  }
  const neg = arr.filter((x) => x < 0).map((x) => -x);
  const pos = arr.filter((x) => x >= 0);
  const n = radixNaoNegativos(neg).reverse().map((x) => -x);
  return [...n, ...radixNaoNegativos(pos)];
}
