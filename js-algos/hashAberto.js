// Tabela hash própria com endereçamento aberto (sondagem linear) e remoção por lápide.
const VAZIO = Symbol('vazio');
const LAPIDE = Symbol('lapide');

// FNV-1a de 32 bits sobre a representação textual da chave.
export function hashFnv(chave) {
  const s = typeof chave === 'string' ? chave : `${typeof chave}:${String(chave)}`;
  let h = 0x811c9dc5;
  for (let i = 0; i < s.length; i++) {
    h ^= s.charCodeAt(i);
    h = Math.imul(h, 0x01000193) >>> 0;
  }
  return h;
}

export class HashAberto {
  #chaves; #valores; #tam = 0; #lapides = 0; #hash;

  constructor(capacidade = 8, hash = hashFnv) {
    this.#hash = hash;
    this.#iniciar(Math.max(4, capacidade));
  }

  #iniciar(cap) {
    this.#chaves = new Array(cap).fill(VAZIO);
    this.#valores = new Array(cap);
    this.#tam = 0;
    this.#lapides = 0;
  }

  get tamanho() { return this.#tam; }
  get capacidade() { return this.#chaves.length; }

  // Índice da chave, ou -1.
  #achar(chave) {
    const cap = this.#chaves.length;
    for (let i = 0, p = this.#hash(chave) % cap; i < cap; i++, p = (p + 1) % cap) {
      const k = this.#chaves[p];
      if (k === VAZIO) return -1;
      if (k !== LAPIDE && Object.is(k, chave)) return p;
    }
    return -1;
  }

  #redimensionar(nova) {
    const antigas = this.#chaves, valores = this.#valores;
    this.#iniciar(nova);
    antigas.forEach((k, i) => { if (k !== VAZIO && k !== LAPIDE) this.definir(k, valores[i]); });
  }

  definir(chave, valor) {
    const existente = this.#achar(chave);
    if (existente >= 0) { this.#valores[existente] = valor; return this; }
    if ((this.#tam + this.#lapides + 1) / this.#chaves.length > 0.7) {
      this.#redimensionar(this.#tam + 1 > this.#chaves.length * 0.35 ? this.#chaves.length * 2 : this.#chaves.length);
    }
    const cap = this.#chaves.length;
    let p = this.#hash(chave) % cap;
    while (this.#chaves[p] !== VAZIO && this.#chaves[p] !== LAPIDE) p = (p + 1) % cap;
    if (this.#chaves[p] === LAPIDE) this.#lapides--;
    this.#chaves[p] = chave;
    this.#valores[p] = valor;
    this.#tam++;
    return this;
  }

  obter(chave) {
    const p = this.#achar(chave);
    return p >= 0 ? this.#valores[p] : undefined;
  }

  tem(chave) { return this.#achar(chave) >= 0; }

  remover(chave) {
    const p = this.#achar(chave);
    if (p < 0) return false;
    this.#chaves[p] = LAPIDE;
    this.#valores[p] = undefined;
    this.#tam--;
    this.#lapides++;
    return true;
  }

  *entradas() {
    for (let i = 0; i < this.#chaves.length; i++) {
      const k = this.#chaves[i];
      if (k !== VAZIO && k !== LAPIDE) yield [k, this.#valores[i]];
    }
  }

  [Symbol.iterator]() { return this.entradas(); }
}
