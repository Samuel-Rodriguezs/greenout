// Árvore geradora mínima (Kruskal) com union-find (compressão + união por tamanho).
export class UniaoBusca {
  constructor(n) {
    this.pai = Array.from({ length: n }, (_, i) => i);
    this.tam = new Array(n).fill(1);
    this.conjuntos = n;
  }

  achar(x) {
    while (this.pai[x] !== x) {
      this.pai[x] = this.pai[this.pai[x]];
      x = this.pai[x];
    }
    return x;
  }

  unir(a, b) {
    let ra = this.achar(a), rb = this.achar(b);
    if (ra === rb) return false;
    if (this.tam[ra] < this.tam[rb]) [ra, rb] = [rb, ra];
    this.pai[rb] = ra;
    this.tam[ra] += this.tam[rb];
    this.conjuntos--;
    return true;
  }
}

// arestas: [[u, v, peso], ...]. Devolve floresta geradora mínima.
export function kruskal(n, arestas) {
  const uf = new UniaoBusca(n);
  const escolhidas = [];
  let peso = 0;
  for (const [u, v, w] of [...arestas].sort((a, b) => a[2] - b[2])) {
    if (uf.unir(u, v)) { escolhidas.push([u, v, w]); peso += w; }
  }
  return { arestas: escolhidas, peso, conexo: uf.conjuntos <= 1 };
}
