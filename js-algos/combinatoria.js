// Geradores preguiçosos de permutações, combinações e afins (generators).

// Permutações em ordem lexicográfica das posições (algoritmo de Heap seria não lexicográfico).
export function* permutacoes(itens, k = itens.length) {
  const n = itens.length;
  if (k < 0 || k > n) return;
  const usado = new Array(n).fill(false);
  const atual = [];
  function* rec() {
    if (atual.length === k) { yield [...atual]; return; }
    for (let i = 0; i < n; i++) {
      if (usado[i]) continue;
      usado[i] = true; atual.push(itens[i]);
      yield* rec();
      atual.pop(); usado[i] = false;
    }
  }
  yield* rec();
}

// Combinações de k elementos, mantendo a ordem original.
export function* combinacoes(itens, k) {
  const n = itens.length;
  if (k < 0 || k > n) return;
  const atual = [];
  function* rec(ini) {
    if (atual.length === k) { yield [...atual]; return; }
    for (let i = ini; i <= n - (k - atual.length); i++) {
      atual.push(itens[i]);
      yield* rec(i + 1);
      atual.pop();
    }
  }
  yield* rec(0);
}

// Todos os subconjuntos (conjunto das partes) por máscara de bits, até 30 elementos.
export function* subconjuntos(itens) {
  const n = itens.length;
  if (n > 30) throw new RangeError('máximo de 30 elementos');
  for (let m = 0; m < 1 << n; m++) yield itens.filter((_, i) => m & (1 << i));
}

// Produto cartesiano de várias listas.
export function* produtoCartesiano(...listas) {
  if (listas.some((l) => l.length === 0)) return;
  const idx = new Array(listas.length).fill(0);
  for (;;) {
    yield idx.map((i, j) => listas[j][i]);
    let p = listas.length - 1;
    while (p >= 0 && ++idx[p] === listas[p].length) idx[p--] = 0;
    if (p < 0) return;
  }
}

// Próxima permutação lexicográfica (in-place num vetor); devolve false se era a última.
export function proximaPermutacao(v) {
  let i = v.length - 2;
  while (i >= 0 && v[i] >= v[i + 1]) i--;
  if (i < 0) return false;
  let j = v.length - 1;
  while (v[j] <= v[i]) j--;
  [v[i], v[j]] = [v[j], v[i]];
  for (let a = i + 1, b = v.length - 1; a < b; a++, b--) [v[a], v[b]] = [v[b], v[a]];
  return true;
}

export const fatorial = (n) => (n <= 1 ? 1 : n * fatorial(n - 1));
