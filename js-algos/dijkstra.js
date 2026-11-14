// Dijkstra com fila de prioridade. grafo[u] = [[v, peso], ...], pesos >= 0.
import { FilaPrioridade } from './filaPrioridade.js';

export function dijkstra(grafo, origem) {
  const dist = new Array(grafo.length).fill(Infinity);
  const pai = new Array(grafo.length).fill(-1);
  dist[origem] = 0;
  const fila = new FilaPrioridade((a, b) => a[0] - b[0], [[0, origem]]);
  while (!fila.vazia) {
    const [d, u] = fila.remover();
    if (d > dist[u]) continue; // entrada obsoleta
    for (const [v, peso] of grafo[u]) {
      if (peso < 0) throw new RangeError('Dijkstra não aceita pesos negativos');
      if (d + peso < dist[v]) {
        dist[v] = d + peso;
        pai[v] = u;
        fila.inserir([dist[v], v]);
      }
    }
  }
  return { dist, pai };
}

// Caminho de origem a destino, ou null se inalcançável.
export function caminhoMinimo(grafo, origem, destino) {
  const { dist, pai } = dijkstra(grafo, origem);
  if (dist[destino] === Infinity) return null;
  const caminho = [];
  for (let x = destino; x !== -1; x = pai[x]) caminho.push(x);
  return { custo: dist[destino], caminho: caminho.reverse() };
}
