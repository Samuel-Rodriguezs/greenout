// Rota mais curta em grafo viário com coordenadas: Dijkstra e A* (heurística haversine).
import { distanciaHaversine } from './haversine.js';

class FilaMin {
  #h = [];
  get tamanho() { return this.#h.length; }
  push(prioridade, valor) {
    const h = this.#h;
    h.push([prioridade, valor]);
    let i = h.length - 1;
    while (i > 0) {
      const p = (i - 1) >> 1;
      if (h[p][0] <= h[i][0]) break;
      [h[p], h[i]] = [h[i], h[p]];
      i = p;
    }
  }
  pop() {
    const h = this.#h;
    const topo = h[0];
    const ultimo = h.pop();
    if (h.length) {
      h[0] = ultimo;
      let i = 0;
      for (;;) {
        const l = 2 * i + 1, r = l + 1;
        let m = i;
        if (l < h.length && h[l][0] < h[m][0]) m = l;
        if (r < h.length && h[r][0] < h[m][0]) m = r;
        if (m === i) break;
        [h[m], h[i]] = [h[i], h[m]];
        i = m;
      }
    }
    return topo;
  }
}

export class GrafoViario {
  #nos = new Map(); // id -> [lat, lon]
  #adj = new Map(); // id -> Map(vizinho -> peso em metros)

  adicionaNo(id, lat, lon) {
    if (this.#nos.has(id)) throw new Error(`nó duplicado: ${id}`);
    this.#nos.set(id, [lat, lon]);
    this.#adj.set(id, new Map());
    return this;
  }

  coordenada(id) { return this.#nos.get(id); }
  get numeroDeNos() { return this.#nos.size; }

  /**
   * Adiciona uma via. Peso padrão = distância haversine (metros). Um peso
   * menor que a distância em linha reta quebraria a admissibilidade do A*,
   * por isso é rejeitado.
   */
  adicionaVia(a, b, { peso, mao = 'dupla' } = {}) {
    for (const id of [a, b]) if (!this.#nos.has(id)) throw new Error(`nó inexistente: ${id}`);
    const reta = distanciaHaversine(...this.#nos.get(a), ...this.#nos.get(b));
    const w = peso ?? reta;
    if (!(w >= reta - 1e-6)) throw new RangeError('peso menor que a distância em linha reta');
    this.#adj.get(a).set(b, w);
    if (mao === 'dupla') this.#adj.get(b).set(a, w);
    return this;
  }

  #busca(origem, destino, heuristica) {
    for (const id of [origem, destino]) if (!this.#nos.has(id)) throw new Error(`nó inexistente: ${id}`);
    const g = new Map([[origem, 0]]);
    const pai = new Map();
    const fechados = new Set();
    const fila = new FilaMin();
    fila.push(heuristica(origem), origem);
    let expandidos = 0;
    while (fila.tamanho) {
      const [, u] = fila.pop();
      if (fechados.has(u)) continue;
      fechados.add(u);
      expandidos++;
      if (u === destino) {
        const caminho = [u];
        while (pai.has(caminho[0])) caminho.unshift(pai.get(caminho[0]));
        return { distancia: g.get(u), caminho, expandidos };
      }
      for (const [v, w] of this.#adj.get(u)) {
        const novo = g.get(u) + w;
        if (novo < (g.get(v) ?? Infinity)) {
          g.set(v, novo);
          pai.set(v, u);
          fila.push(novo + heuristica(v), v);
        }
      }
    }
    return { distancia: Infinity, caminho: [], expandidos };
  }

  dijkstra(origem, destino) {
    return this.#busca(origem, destino, () => 0);
  }

  aEstrela(origem, destino) {
    const alvo = this.#nos.get(destino);
    if (!alvo) throw new Error(`nó inexistente: ${destino}`);
    return this.#busca(origem, destino, (id) => distanciaHaversine(...this.#nos.get(id), ...alvo));
  }
}
