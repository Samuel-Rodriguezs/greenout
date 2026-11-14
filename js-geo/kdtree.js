// k-d tree estática (k dimensões) construída pela mediana, com busca de vizinhos.

export class KDTree {
  #raiz;
  #k;

  /** `pontos`: arrays numéricos de mesmo tamanho (ex.: [x, y]). */
  constructor(pontos) {
    if (pontos.length === 0) {
      this.#k = 0;
      this.#raiz = null;
      return;
    }
    this.#k = pontos[0].length;
    if (this.#k === 0 || pontos.some((p) => p.length !== this.#k)) {
      throw new RangeError('todos os pontos devem ter a mesma dimensão (>= 1)');
    }
    this.#raiz = this.#constroi([...pontos], 0);
  }

  get tamanho() { return this.#contar(this.#raiz); }

  #contar(no) { return no ? 1 + this.#contar(no.esq) + this.#contar(no.dir) : 0; }

  #constroi(pontos, prof) {
    if (pontos.length === 0) return null;
    const eixo = prof % this.#k;
    pontos.sort((a, b) => a[eixo] - b[eixo]);
    const m = pontos.length >> 1;
    return {
      ponto: pontos[m],
      eixo,
      esq: this.#constroi(pontos.slice(0, m), prof + 1),
      dir: this.#constroi(pontos.slice(m + 1), prof + 1),
    };
  }

  static #dist2(a, b) {
    let s = 0;
    for (let i = 0; i < a.length; i++) s += (a[i] - b[i]) ** 2;
    return s;
  }

  #confere(alvo) {
    if (alvo.length !== this.#k) throw new RangeError('dimensão do alvo incompatível');
  }

  /** Ponto mais próximo do alvo, ou null se a árvore estiver vazia. */
  maisProximo(alvo) {
    return this.kMaisProximos(alvo, 1)[0] ?? null;
  }

  /** Os `k` pontos mais próximos, do mais perto ao mais longe. */
  kMaisProximos(alvo, k) {
    if (!this.#raiz || k <= 0) return [];
    this.#confere(alvo);
    const melhores = []; // { ponto, d2 } ordenado crescente
    const visita = (no) => {
      if (!no) return;
      const d2 = KDTree.#dist2(no.ponto, alvo);
      if (melhores.length < k || d2 < melhores[melhores.length - 1].d2) {
        melhores.push({ ponto: no.ponto, d2 });
        melhores.sort((a, b) => a.d2 - b.d2);
        if (melhores.length > k) melhores.pop();
      }
      const diff = alvo[no.eixo] - no.ponto[no.eixo];
      const [perto, longe] = diff < 0 ? [no.esq, no.dir] : [no.dir, no.esq];
      visita(perto);
      if (melhores.length < k || diff * diff < melhores[melhores.length - 1].d2) visita(longe);
    };
    visita(this.#raiz);
    return melhores.map((m) => m.ponto);
  }

  /** Todos os pontos dentro do hiper-retângulo [min, max] (bordas incluídas). */
  buscaIntervalo(min, max) {
    const achados = [];
    const visita = (no) => {
      if (!no) return;
      if (no.ponto.every((v, i) => v >= min[i] && v <= max[i])) achados.push(no.ponto);
      if (min[no.eixo] <= no.ponto[no.eixo]) visita(no.esq);
      if (max[no.eixo] >= no.ponto[no.eixo]) visita(no.dir);
    };
    visita(this.#raiz);
    return achados;
  }
}
