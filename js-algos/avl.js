// Árvore AVL (autobalanceada) funcional: nós imutáveis, operações devolvem nova raiz internamente.
class No {
  constructor(chave, valor, esq = null, dir = null) {
    this.chave = chave;
    this.valor = valor;
    this.esq = esq;
    this.dir = dir;
    this.altura = 1 + Math.max(No.alt(esq), No.alt(dir));
  }

  static alt(n) { return n ? n.altura : 0; }
  static fb(n) { return n ? No.alt(n.esq) - No.alt(n.dir) : 0; }
}

const rotDir = (y) => new No(y.esq.chave, y.esq.valor, y.esq.esq, new No(y.chave, y.valor, y.esq.dir, y.dir));
const rotEsq = (x) => new No(x.dir.chave, x.dir.valor, new No(x.chave, x.valor, x.esq, x.dir.esq), x.dir.dir);

function balancear(n) {
  const fb = No.fb(n);
  if (fb > 1) {
    if (No.fb(n.esq) < 0) n = new No(n.chave, n.valor, rotEsq(n.esq), n.dir);
    return rotDir(n);
  }
  if (fb < -1) {
    if (No.fb(n.dir) > 0) n = new No(n.chave, n.valor, n.esq, rotDir(n.dir));
    return rotEsq(n);
  }
  return n;
}

export class Avl {
  #raiz = null; #tam = 0; #cmp;

  constructor(cmp = (a, b) => (a < b ? -1 : a > b ? 1 : 0)) { this.#cmp = cmp; }

  get tamanho() { return this.#tam; }
  get altura() { return No.alt(this.#raiz); }

  inserir(chave, valor = chave) {
    let novo = false;
    const ins = (n) => {
      if (!n) { novo = true; return new No(chave, valor); }
      const c = this.#cmp(chave, n.chave);
      if (c === 0) return new No(n.chave, valor, n.esq, n.dir);
      return balancear(c < 0 ? new No(n.chave, n.valor, ins(n.esq), n.dir) : new No(n.chave, n.valor, n.esq, ins(n.dir)));
    };
    this.#raiz = ins(this.#raiz);
    if (novo) this.#tam++;
    return this;
  }

  obter(chave) {
    for (let n = this.#raiz; n;) {
      const c = this.#cmp(chave, n.chave);
      if (c === 0) return n.valor;
      n = c < 0 ? n.esq : n.dir;
    }
    return undefined;
  }

  tem(chave) {
    for (let n = this.#raiz; n;) {
      const c = this.#cmp(chave, n.chave);
      if (c === 0) return true;
      n = c < 0 ? n.esq : n.dir;
    }
    return false;
  }

  remover(chave) {
    let achou = false;
    const menor = (n) => { while (n.esq) n = n.esq; return n; };
    const rem = (n, k) => {
      if (!n) return null;
      const c = this.#cmp(k, n.chave);
      if (c < 0) return balancear(new No(n.chave, n.valor, rem(n.esq, k), n.dir));
      if (c > 0) return balancear(new No(n.chave, n.valor, n.esq, rem(n.dir, k)));
      achou = true;
      if (!n.esq) return n.dir;
      if (!n.dir) return n.esq;
      const suc = menor(n.dir);
      const semSuc = (m) => (m.esq ? balancear(new No(m.chave, m.valor, semSuc(m.esq), m.dir)) : m.dir);
      return balancear(new No(suc.chave, suc.valor, n.esq, semSuc(n.dir)));
    };
    this.#raiz = rem(this.#raiz, chave);
    if (achou) this.#tam--;
    return achou;
  }

  minimo() {
    let n = this.#raiz;
    if (!n) return undefined;
    while (n.esq) n = n.esq;
    return [n.chave, n.valor];
  }

  maximo() {
    let n = this.#raiz;
    if (!n) return undefined;
    while (n.dir) n = n.dir;
    return [n.chave, n.valor];
  }

  // Verifica invariantes (ordem e balanceamento); útil nos testes.
  valida() {
    const ver = (n, lo, hi) => {
      if (!n) return 0;
      if (lo !== undefined && this.#cmp(n.chave, lo) <= 0) throw new Error('ordem violada');
      if (hi !== undefined && this.#cmp(n.chave, hi) >= 0) throw new Error('ordem violada');
      const he = ver(n.esq, lo, n.chave), hd = ver(n.dir, n.chave, hi);
      if (Math.abs(he - hd) > 1) throw new Error('desbalanceada');
      return 1 + Math.max(he, hd);
    };
    ver(this.#raiz);
    return true;
  }

  *entradas() {
    function* em(n) { if (n) { yield* em(n.esq); yield [n.chave, n.valor]; yield* em(n.dir); } }
    yield* em(this.#raiz);
  }

  [Symbol.iterator]() { return this.entradas(); }
}
