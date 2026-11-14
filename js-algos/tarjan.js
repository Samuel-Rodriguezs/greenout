// Componentes fortemente conexas (Tarjan), pontes e pontos de articulação.

// grafo direcionado: grafo[u] = [v...]. Devolve SCCs em ordem topológica reversa.
export function componentesFortes(grafo) {
  const n = grafo.length;
  const idx = new Array(n).fill(-1);
  const baixo = new Array(n).fill(0);
  const naPilha = new Array(n).fill(false);
  const pilha = [];
  const res = [];
  let contador = 0;

  const visitar = (u) => {
    idx[u] = baixo[u] = contador++;
    pilha.push(u);
    naPilha[u] = true;
    for (const v of grafo[u]) {
      if (idx[v] === -1) {
        visitar(v);
        baixo[u] = Math.min(baixo[u], baixo[v]);
      } else if (naPilha[v]) {
        baixo[u] = Math.min(baixo[u], idx[v]);
      }
    }
    if (baixo[u] === idx[u]) {
      const comp = [];
      let w;
      do { w = pilha.pop(); naPilha[w] = false; comp.push(w); } while (w !== u);
      res.push(comp.sort((a, b) => a - b));
    }
  };
  for (let u = 0; u < n; u++) if (idx[u] === -1) visitar(u);
  return res;
}

// grafo não direcionado simples: devolve { pontes, articulacoes }.
export function pontesEArticulacoes(grafo) {
  const n = grafo.length;
  const tin = new Array(n).fill(-1);
  const low = new Array(n).fill(0);
  const pontes = [];
  const art = new Set();
  let t = 0;
  const visitar = (u, pai) => {
    tin[u] = low[u] = t++;
    let filhos = 0;
    for (const v of grafo[u]) {
      if (v === pai) continue;
      if (tin[v] !== -1) {
        low[u] = Math.min(low[u], tin[v]);
      } else {
        visitar(v, u);
        low[u] = Math.min(low[u], low[v]);
        if (low[v] > tin[u]) pontes.push([Math.min(u, v), Math.max(u, v)]);
        if (low[v] >= tin[u] && pai !== -1) art.add(u);
        filhos++;
      }
    }
    if (pai === -1 && filhos > 1) art.add(u);
  };
  for (let u = 0; u < n; u++) if (tin[u] === -1) visitar(u, -1);
  return {
    pontes: pontes.sort((a, b) => a[0] - b[0] || a[1] - b[1]),
    articulacoes: [...art].sort((a, b) => a - b),
  };
}
