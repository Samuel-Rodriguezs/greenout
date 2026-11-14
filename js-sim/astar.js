// Pathfinding A* em grade (0 = livre, 1 = parede). Heap binário como fila de prioridade.

class Heap {
  constructor() { this.a = []; }
  get tamanho() { return this.a.length; }
  push(item) {
    const a = this.a;
    a.push(item);
    let i = a.length - 1;
    while (i > 0) {
      const p = (i - 1) >> 1;
      if (this._menor(a[p], a[i]) || this._igual(a[p], a[i])) break;
      [a[p], a[i]] = [a[i], a[p]];
      i = p;
    }
  }
  pop() {
    const a = this.a;
    const topo = a[0];
    const ultimo = a.pop();
    if (a.length) {
      a[0] = ultimo;
      let i = 0;
      for (;;) {
        const l = 2 * i + 1;
        const r = l + 1;
        let m = i;
        if (l < a.length && this._menor(a[l], a[m])) m = l;
        if (r < a.length && this._menor(a[r], a[m])) m = r;
        if (m === i) break;
        [a[m], a[i]] = [a[i], a[m]];
        i = m;
      }
    }
    return topo;
  }
  // ordena por f, depois por h (prefere nós mais próximos do destino)
  _menor(x, y) { return x.f < y.f || (x.f === y.f && x.h < y.h); }
  _igual(x, y) { return x.f === y.f && x.h === y.h; }
}

const ORTOGONAIS = [[0, 1], [1, 0], [0, -1], [-1, 0]];
const DIAGONAIS = [[1, 1], [1, -1], [-1, 1], [-1, -1]];

/**
 * Busca o menor caminho de `inicio` a `fim` ([linha, coluna]).
 * opções: diagonal (8 direções, sem "cortar quina"), custos (matriz de custo de entrada, >=1).
 * Retorna {caminho:[[l,c],...], custo, visitados} ou null se inalcançável.
 */
export function aEstrela(grade, inicio, fim, { diagonal = false, custos = null } = {}) {
  const linhas = grade.length;
  const colunas = grade[0].length;
  const dentro = (l, c) => l >= 0 && c >= 0 && l < linhas && c < colunas;
  for (const [l, c] of [inicio, fim]) {
    if (!dentro(l, c) || grade[l][c] === 1) return null;
  }
  const id = (l, c) => l * colunas + c;
  const h = (l, c) => {
    const dl = Math.abs(l - fim[0]);
    const dc = Math.abs(c - fim[1]);
    return diagonal ? (dl + dc) + (Math.SQRT2 - 2) * Math.min(dl, dc) : dl + dc;
  };
  const g = new Map([[id(...inicio), 0]]);
  const pai = new Map();
  const fechado = new Set();
  const aberto = new Heap();
  aberto.push({ l: inicio[0], c: inicio[1], g: 0, h: h(...inicio), f: h(...inicio) });
  let visitados = 0;

  while (aberto.tamanho) {
    const atual = aberto.pop();
    const k = id(atual.l, atual.c);
    if (fechado.has(k)) continue;
    fechado.add(k);
    visitados++;
    if (atual.l === fim[0] && atual.c === fim[1]) {
      const caminho = [];
      for (let n = k; n !== undefined; n = pai.get(n)) caminho.push([Math.floor(n / colunas), n % colunas]);
      return { caminho: caminho.reverse(), custo: atual.g, visitados };
    }
    const movs = diagonal ? [...ORTOGONAIS, ...DIAGONAIS] : ORTOGONAIS;
    for (const [dl, dc] of movs) {
      const nl = atual.l + dl;
      const nc = atual.c + dc;
      if (!dentro(nl, nc) || grade[nl][nc] === 1) continue;
      const ehDiag = dl !== 0 && dc !== 0;
      // não permite atravessar a quina de uma parede
      if (ehDiag && (grade[atual.l + dl][atual.c] === 1 || grade[atual.l][atual.c + dc] === 1)) continue;
      const nk = id(nl, nc);
      if (fechado.has(nk)) continue;
      const passoCusto = (ehDiag ? Math.SQRT2 : 1) * (custos ? custos[nl][nc] : 1);
      const ng = atual.g + passoCusto;
      if (ng < (g.get(nk) ?? Infinity)) {
        g.set(nk, ng);
        pai.set(nk, k);
        const hh = h(nl, nc);
        aberto.push({ l: nl, c: nc, g: ng, h: hh, f: ng + hh });
      }
    }
  }
  return null;
}

/** Converte um mapa de texto ('#' parede, '.' livre, 'S' início, 'G' destino). */
export function lerMapa(linhas) {
  let inicio = null;
  let fim = null;
  const grade = linhas.map((s, l) => [...s].map((ch, c) => {
    if (ch === 'S') inicio = [l, c];
    if (ch === 'G') fim = [l, c];
    return ch === '#' ? 1 : 0;
  }));
  return { grade, inicio, fim };
}
