// BFS e DFS sobre grafo como lista de adjacência: grafo[u] = [vizinhos...].

// Ordem de visita da BFS a partir de s.
export function bfs(grafo, s) {
  const visto = new Set([s]);
  const fila = [s];
  const ordem = [];
  for (let i = 0; i < fila.length; i++) {
    const u = fila[i];
    ordem.push(u);
    for (const v of grafo[u] ?? []) {
      if (!visto.has(v)) { visto.add(v); fila.push(v); }
    }
  }
  return ordem;
}

// Menor caminho (em arestas) de s a t, ou null.
export function menorCaminho(grafo, s, t) {
  const pai = new Map([[s, null]]);
  const fila = [s];
  for (let i = 0; i < fila.length; i++) {
    const u = fila[i];
    if (u === t) break;
    for (const v of grafo[u] ?? []) {
      if (!pai.has(v)) { pai.set(v, u); fila.push(v); }
    }
  }
  if (!pai.has(t)) return null;
  const caminho = [];
  for (let x = t; x !== null; x = pai.get(x)) caminho.push(x);
  return caminho.reverse();
}

// DFS iterativa (pré-ordem), respeitando a ordem dos vizinhos.
export function dfs(grafo, s) {
  const visto = new Set();
  const pilha = [s];
  const ordem = [];
  while (pilha.length) {
    const u = pilha.pop();
    if (visto.has(u)) continue;
    visto.add(u);
    ordem.push(u);
    const viz = grafo[u] ?? [];
    for (let i = viz.length - 1; i >= 0; i--) if (!visto.has(viz[i])) pilha.push(viz[i]);
  }
  return ordem;
}

// Componentes conexas de um grafo não direcionado com n vértices.
export function componentes(grafo) {
  const visto = new Set();
  const res = [];
  for (let u = 0; u < grafo.length; u++) {
    if (visto.has(u)) continue;
    const comp = dfs(grafo, u);
    comp.forEach((x) => visto.add(x));
    res.push(comp.sort((a, b) => a - b));
  }
  return res;
}

// Detecta ciclo em grafo direcionado (cores branco/cinza/preto).
export function temCiclo(grafo) {
  const cor = new Array(grafo.length).fill(0);
  const visitar = (u) => {
    cor[u] = 1;
    for (const v of grafo[u]) {
      if (cor[v] === 1 || (cor[v] === 0 && visitar(v))) return true;
    }
    cor[u] = 2;
    return false;
  };
  return grafo.some((_, u) => cor[u] === 0 && visitar(u));
}
