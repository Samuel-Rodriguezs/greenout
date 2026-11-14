// Fila de prioridade (min-heap binário) com comparador configurável.
export class FilaPrioridade {
  #v = [];
  #cmp;

  constructor(cmp = (a, b) => a - b, itens = []) {
    this.#cmp = cmp;
    for (const x of itens) this.inserir(x);
  }

  get tamanho() { return this.#v.length; }
  get vazia() { return this.#v.length === 0; }

  espiar() { return this.#v[0]; }

  inserir(x) {
    const v = this.#v;
    v.push(x);
    let i = v.length - 1;
    while (i > 0) {
      const pai = (i - 1) >> 1;
      if (this.#cmp(v[i], v[pai]) >= 0) break;
      [v[i], v[pai]] = [v[pai], v[i]];
      i = pai;
    }
    return this;
  }

  // Remove e devolve o menor elemento; undefined se vazia.
  remover() {
    const v = this.#v;
    if (v.length === 0) return undefined;
    const topo = v[0];
    const ultimo = v.pop();
    if (v.length > 0) {
      v[0] = ultimo;
      let i = 0;
      for (;;) {
        const l = 2 * i + 1, r = l + 1;
        let menor = i;
        if (l < v.length && this.#cmp(v[l], v[menor]) < 0) menor = l;
        if (r < v.length && this.#cmp(v[r], v[menor]) < 0) menor = r;
        if (menor === i) break;
        [v[i], v[menor]] = [v[menor], v[i]];
        i = menor;
      }
    }
    return topo;
  }

  *[Symbol.iterator]() { // esvazia a fila em ordem
    while (!this.vazia) yield this.remover();
  }
}
