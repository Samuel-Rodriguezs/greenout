// Quadtree de pontos com capacidade por nó e profundidade máxima.
import { contemPonto, intersecta, criaBBox, distanciaAoPonto } from './bbox.js';

export class QuadTree {
  #limites;
  #capacidade;
  #profMax;
  #pontos = [];
  #filhos = null;
  #tamanho = 0;

  constructor(limites, { capacidade = 4, profundidadeMax = 16 } = {}, profundidade = 0) {
    this.#limites = limites;
    this.#capacidade = capacidade;
    this.#profMax = profundidadeMax;
    this.profundidade = profundidade;
  }

  get tamanho() { return this.#tamanho; }

  /** Insere {x, y, dados?}. Retorna false se o ponto cai fora dos limites. */
  insere(ponto) {
    if (!contemPonto(this.#limites, [ponto.x, ponto.y])) return false;
    if (!this.#filhos) {
      if (this.#pontos.length < this.#capacidade || this.profundidade >= this.#profMax) {
        this.#pontos.push(ponto);
        this.#tamanho++;
        return true;
      }
      this.#divide();
    }
    this.#tamanho++;
    for (const f of this.#filhos) if (f.insere(ponto)) return true;
    this.#tamanho--; // inalcançável: os filhos cobrem todo o pai
    return false;
  }

  #divide() {
    const { minX, minY, maxX, maxY } = this.#limites;
    const mx = (minX + maxX) / 2, my = (minY + maxY) / 2;
    const opts = { capacidade: this.#capacidade, profundidadeMax: this.#profMax };
    const d = this.profundidade + 1;
    this.#filhos = [
      new QuadTree(criaBBox(minX, minY, mx, my), opts, d),
      new QuadTree(criaBBox(mx, minY, maxX, my), opts, d),
      new QuadTree(criaBBox(minX, my, mx, maxY), opts, d),
      new QuadTree(criaBBox(mx, my, maxX, maxY), opts, d),
    ];
    const antigos = this.#pontos;
    this.#pontos = [];
    this.#tamanho = 0;
    for (const p of antigos) {
      for (const f of this.#filhos) if (f.insere(p)) { this.#tamanho++; break; }
    }
  }

  /** Pontos dentro do retângulo (bordas incluídas). */
  buscaRetangulo(r, achados = []) {
    if (!intersecta(this.#limites, r)) return achados;
    for (const p of this.#pontos) if (contemPonto(r, [p.x, p.y])) achados.push(p);
    if (this.#filhos) for (const f of this.#filhos) f.buscaRetangulo(r, achados);
    return achados;
  }

  /** Pontos a até `raio` do centro (distância euclidiana). */
  buscaRaio(cx, cy, raio) {
    const caixa = criaBBox(cx - raio, cy - raio, cx + raio, cy + raio);
    return this.buscaRetangulo(caixa).filter((p) => Math.hypot(p.x - cx, p.y - cy) <= raio);
  }

  /** Vizinho mais próximo com poda por distância à caixa; null se vazia. */
  maisProximo(x, y) {
    let melhor = null, melhorD = Infinity;
    const visita = (no) => {
      if (no.#tamanho === 0 || distanciaAoPonto(no.#limites, [x, y]) >= melhorD) return;
      for (const p of no.#pontos) {
        const d = Math.hypot(p.x - x, p.y - y);
        if (d < melhorD) { melhorD = d; melhor = p; }
      }
      if (no.#filhos) {
        [...no.#filhos]
          .sort((a, b) => distanciaAoPonto(a.#limites, [x, y]) - distanciaAoPonto(b.#limites, [x, y]))
          .forEach(visita);
      }
    };
    visita(this);
    return melhor;
  }
}
