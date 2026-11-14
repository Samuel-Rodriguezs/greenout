// Ordenação topológica (algoritmo de Kahn). grafo[u] = [v, ...] significa u -> v.
// Devolve null se houver ciclo. Desempata pelo menor índice (resultado determinístico).
import { FilaPrioridade } from './filaPrioridade.js';

export function ordenacaoTopologica(grafo) {
  const grau = new Array(grafo.length).fill(0);
  for (const vizinhos of grafo) for (const v of vizinhos) grau[v]++;
  const prontos = new FilaPrioridade(undefined, grau.flatMap((g, i) => (g === 0 ? [i] : [])));
  const ordem = [];
  while (!prontos.vazia) {
    const u = prontos.remover();
    ordem.push(u);
    for (const v of grafo[u]) if (--grau[v] === 0) prontos.inserir(v);
  }
  return ordem.length === grafo.length ? ordem : null;
}

// Ordem de execução de tarefas nomeadas: deps = { tarefa: [dependências] }.
export function ordemDeTarefas(deps) {
  const nomes = [...new Set(Object.entries(deps).flatMap(([k, v]) => [k, ...v]))].sort();
  const idx = new Map(nomes.map((n, i) => [n, i]));
  const grafo = nomes.map(() => []);
  for (const [tarefa, ds] of Object.entries(deps)) {
    for (const d of ds) grafo[idx.get(d)].push(idx.get(tarefa));
  }
  const ordem = ordenacaoTopologica(grafo);
  return ordem && ordem.map((i) => nomes[i]);
}
