// Cache LRU (menos recentemente usado) em O(1), apoiado na ordem de inserção do Map.

export class LRUCache {
  #capacidade;
  #mapa = new Map();

  constructor(capacidade) {
    if (!Number.isInteger(capacidade) || capacidade < 1) {
      throw new RangeError('capacidade deve ser um inteiro >= 1');
    }
    this.#capacidade = capacidade;
  }

  get tamanho() { return this.#mapa.size; }

  get(chave) {
    if (!this.#mapa.has(chave)) return undefined;
    const valor = this.#mapa.get(chave);
    this.#mapa.delete(chave);
    this.#mapa.set(chave, valor); // move para "mais recente"
    return valor;
  }

  /** Consulta sem alterar a ordem de uso. */
  espiar(chave) {
    return this.#mapa.get(chave);
  }

  has(chave) {
    return this.#mapa.has(chave);
  }

  set(chave, valor) {
    if (this.#mapa.has(chave)) this.#mapa.delete(chave);
    else if (this.#mapa.size >= this.#capacidade) {
      const maisAntiga = this.#mapa.keys().next().value;
      this.#mapa.delete(maisAntiga);
    }
    this.#mapa.set(chave, valor);
    return this;
  }

  delete(chave) {
    return this.#mapa.delete(chave);
  }

  /** Chaves da mais antiga para a mais recente. */
  chaves() {
    return [...this.#mapa.keys()];
  }
}
