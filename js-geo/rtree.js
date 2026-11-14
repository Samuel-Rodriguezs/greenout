// R-tree simples: inserção com menor ampliação de área e divisão por ordenação
// no eixo mais longo; busca por retângulo.
import { criaBBox, uniao, areaBBox, intersecta } from './bbox.js';

export class RTree {
  #max;
  #min;
  #raiz;
  #n = 0;

  constructor(maxEntradas = 4) {
    if (maxEntradas < 3) throw new RangeError('maxEntradas deve ser >= 3');
    this.#max = maxEntradas;
    this.#min = Math.max(1, Math.floor(maxEntradas / 2));
    this.#raiz = { folha: true, filhos: [], caixa: null };
  }

  get tamanho() { return this.#n; }

  get altura() {
    let h = 1, no = this.#raiz;
    while (!no.folha) { h++; no = no.filhos[0]; }
    return h;
  }

  /** Insere um item associado a uma caixa. */
  insere(caixa, item) {
    const irmao = this.#insere(this.#raiz, { caixa, item });
    if (irmao) {
      const antigaRaiz = this.#raiz;
      this.#raiz = {
        folha: false,
        filhos: [antigaRaiz, irmao],
        caixa: uniao(antigaRaiz.caixa, irmao.caixa),
      };
    }
    this.#n++;
  }

  insereXY(x, y, item) { this.insere(criaBBox(x, y, x, y), item); }

  #insere(no, entrada) {
    if (no.folha) {
      no.filhos.push(entrada);
    } else {
      const alvo = this.#escolhe(no, entrada.caixa);
      const irmao = this.#insere(alvo, entrada);
      if (irmao) no.filhos.push(irmao);
    }
    no.caixa = no.caixa ? uniao(no.caixa, entrada.caixa) : entrada.caixa;
    return no.filhos.length > this.#max ? this.#divide(no) : null;
  }

  #escolhe(no, caixa) {
    let melhor = null, melhorGanho = Infinity, melhorArea = Infinity;
    for (const f of no.filhos) {
      const area = areaBBox(f.caixa);
      const ganho = areaBBox(uniao(f.caixa, caixa)) - area;
      if (ganho < melhorGanho || (ganho === melhorGanho && area < melhorArea)) {
        melhor = f; melhorGanho = ganho; melhorArea = area;
      }
    }
    return melhor;
  }

  #divide(no) {
    const c = no.caixa;
    const usaX = c.maxX - c.minX >= c.maxY - c.minY;
    const centro = (e) => (usaX ? e.caixa.minX + e.caixa.maxX : e.caixa.minY + e.caixa.maxY);
    const ordenados = [...no.filhos].sort((a, b) => centro(a) - centro(b));
    const corte = Math.max(this.#min, ordenados.length >> 1);
    no.filhos = ordenados.slice(0, corte);
    const irmao = { folha: no.folha, filhos: ordenados.slice(corte), caixa: null };
    no.caixa = RTree.#caixaDe(no.filhos);
    irmao.caixa = RTree.#caixaDe(irmao.filhos);
    return irmao;
  }

  static #caixaDe(entradas) {
    return entradas.map((e) => e.caixa).reduce((a, b) => uniao(a, b));
  }

  /** Itens cujas caixas intersectam `area` (tocar a borda conta). */
  busca(area) {
    const achados = [];
    const visita = (no) => {
      if (!no.caixa || !intersecta(no.caixa, area)) return;
      for (const f of no.filhos) {
        if (no.folha) { if (intersecta(f.caixa, area)) achados.push(f.item); } else visita(f);
      }
    };
    visita(this.#raiz);
    return achados;
  }
}
