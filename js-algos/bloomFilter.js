// Filtro de Bloom: pertinência probabilística (sem falsos negativos).
import { hashFnv } from './hashAberto.js';

export class BloomFilter {
  #bits; #m; #k; #inseridos = 0;

  // m = bits, k = nº de funções hash.
  constructor(m = 1024, k = 3) {
    if (!Number.isInteger(m) || m < 1 || !Number.isInteger(k) || k < 1) throw new RangeError('parâmetros inválidos');
    this.#m = m;
    this.#k = k;
    this.#bits = new Uint8Array(Math.ceil(m / 8));
  }

  // Dimensiona para n itens e taxa de falso positivo p.
  static para(n, p = 0.01) {
    const m = Math.ceil((-n * Math.log(p)) / Math.LN2 ** 2);
    const k = Math.max(1, Math.round((m / n) * Math.LN2));
    return new BloomFilter(m, k);
  }

  // Duplo hashing: h1 + i*h2.
  #posicoes(item) {
    const s = String(item);
    const h1 = hashFnv(s);
    const h2 = hashFnv(s + '\u0001salt') | 1;
    return Array.from({ length: this.#k }, (_, i) => ((h1 + Math.imul(i, h2)) >>> 0) % this.#m);
  }

  adicionar(item) {
    for (const p of this.#posicoes(item)) this.#bits[p >> 3] |= 1 << (p & 7);
    this.#inseridos++;
    return this;
  }

  // false = certamente ausente; true = provavelmente presente.
  talvezTenha(item) {
    return this.#posicoes(item).every((p) => (this.#bits[p >> 3] & (1 << (p & 7))) !== 0);
  }

  get inseridos() { return this.#inseridos; }

  // Estimativa da taxa de falso positivo atual.
  get taxaFalsoPositivo() {
    return (1 - Math.exp((-this.#k * this.#inseridos) / this.#m)) ** this.#k;
  }
}
