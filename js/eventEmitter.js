// EventEmitter mínimo: on, once, off, emit.

export class EventEmitter {
  #ouvintes = new Map();

  on(evento, ouvinte) {
    if (typeof ouvinte !== 'function') throw new TypeError('ouvinte deve ser função');
    if (!this.#ouvintes.has(evento)) this.#ouvintes.set(evento, []);
    this.#ouvintes.get(evento).push({ ouvinte, uma: false });
    return this;
  }

  once(evento, ouvinte) {
    this.on(evento, ouvinte);
    const lista = this.#ouvintes.get(evento);
    lista[lista.length - 1].uma = true;
    return this;
  }

  /** Remove uma ocorrência do ouvinte; sem ouvinte, remove todos do evento. */
  off(evento, ouvinte) {
    const lista = this.#ouvintes.get(evento);
    if (!lista) return this;
    if (ouvinte === undefined) {
      this.#ouvintes.delete(evento);
      return this;
    }
    const i = lista.findIndex((e) => e.ouvinte === ouvinte);
    if (i !== -1) lista.splice(i, 1);
    if (lista.length === 0) this.#ouvintes.delete(evento);
    return this;
  }

  /** Dispara o evento; devolve true se havia ouvintes. */
  emit(evento, ...args) {
    const lista = this.#ouvintes.get(evento);
    if (!lista || lista.length === 0) {
      if (evento === 'erro') throw args[0] instanceof Error ? args[0] : new Error('erro não tratado');
      return false;
    }
    // Cópia: ouvintes podem se remover ou registrar outros durante a emissão.
    for (const entrada of [...lista]) {
      if (entrada.uma) this.off(evento, entrada.ouvinte);
      entrada.ouvinte.apply(this, args);
    }
    return true;
  }

  contarOuvintes(evento) {
    return this.#ouvintes.get(evento)?.length ?? 0;
  }
}
