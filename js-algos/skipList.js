// Skip list ordenada (mapa chave -> valor) com níveis aleatórios.
// O gerador aleatório é injetável para testes determinísticos.
class No {
  constructor(chave, valor, nivel) {
    this.chave = chave;
    this.valor = valor;
    this.prox = new Array(nivel).fill(null);
  }
}

export class SkipList {
  #cabeca; #nivelMax; #p; #rand; #cmp; #nivel = 1; #tam = 0;

  constructor({ nivelMax = 16, p = 0.5, rand = Math.random, cmp = (a, b) => (a < b ? -1 : a > b ? 1 : 0) } = {}) {
    this.#nivelMax = nivelMax;
    this.#p = p;
    this.#rand = rand;
    this.#cmp = cmp;
    this.#cabeca = new No(undefined, undefined, nivelMax);
  }

  get tamanho() { return this.#tam; }

  #nivelAleatorio() {
    let n = 1;
    while (n < this.#nivelMax && this.#rand() < this.#p) n++;
    return n;
  }

  // Predecessores em cada nível.
  #predecessores(chave) {
    const upd = new Array(this.#nivelMax).fill(this.#cabeca);
    let x = this.#cabeca;
    for (let i = this.#nivel - 1; i >= 0; i--) {
      while (x.prox[i] && this.#cmp(x.prox[i].chave, chave) < 0) x = x.prox[i];
      upd[i] = x;
    }
    return { upd, candidato: x.prox[0] };
  }

  definir(chave, valor) {
    const { upd, candidato } = this.#predecessores(chave);
    if (candidato && this.#cmp(candidato.chave, chave) === 0) { candidato.valor = valor; return this; }
    const nivel = this.#nivelAleatorio();
    if (nivel > this.#nivel) this.#nivel = nivel;
    const no = new No(chave, valor, nivel);
    for (let i = 0; i < nivel; i++) {
      no.prox[i] = upd[i].prox[i];
      upd[i].prox[i] = no;
    }
    this.#tam++;
    return this;
  }

  obter(chave) {
    const { candidato } = this.#predecessores(chave);
    return candidato && this.#cmp(candidato.chave, chave) === 0 ? candidato.valor : undefined;
  }

  tem(chave) {
    const { candidato } = this.#predecessores(chave);
    return !!candidato && this.#cmp(candidato.chave, chave) === 0;
  }

  remover(chave) {
    const { upd, candidato } = this.#predecessores(chave);
    if (!candidato || this.#cmp(candidato.chave, chave) !== 0) return false;
    for (let i = 0; i < this.#nivel; i++) {
      if (upd[i].prox[i] !== candidato) break;
      upd[i].prox[i] = candidato.prox[i];
    }
    while (this.#nivel > 1 && this.#cabeca.prox[this.#nivel - 1] === null) this.#nivel--;
    this.#tam--;
    return true;
  }

  // Primeira entrada com chave >= dada.
  primeiroMaiorOuIgual(chave) {
    const { candidato } = this.#predecessores(chave);
    return candidato ? [candidato.chave, candidato.valor] : undefined;
  }

  *entradas() {
    for (let x = this.#cabeca.prox[0]; x; x = x.prox[0]) yield [x.chave, x.valor];
  }

  // Entradas com lo <= chave < hi.
  *faixa(lo, hi) {
    const { candidato } = this.#predecessores(lo);
    for (let x = candidato; x && this.#cmp(x.chave, hi) < 0; x = x.prox[0]) yield [x.chave, x.valor];
  }

  [Symbol.iterator]() { return this.entradas(); }
}
