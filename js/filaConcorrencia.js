// Fila de tarefas assíncronas com limite de concorrência.

export class FilaConcorrencia {
  #limite;
  #ativas = 0;
  #espera = [];
  #ociosos = [];

  constructor(limite) {
    if (!Number.isInteger(limite) || limite < 1) {
      throw new RangeError('limite deve ser um inteiro >= 1');
    }
    this.#limite = limite;
  }

  get ativas() { return this.#ativas; }
  get pendentes() { return this.#espera.length; }

  /** Enfileira uma função que retorna promessa; devolve promessa do resultado dela. */
  adicionar(tarefa) {
    return new Promise((resolve, reject) => {
      this.#espera.push({ tarefa, resolve, reject });
      this.#proxima();
    });
  }

  /** Resolve quando não há tarefas ativas nem pendentes. */
  aguardarOciosa() {
    if (this.#ativas === 0 && this.#espera.length === 0) return Promise.resolve();
    return new Promise((resolve) => this.#ociosos.push(resolve));
  }

  #proxima() {
    while (this.#ativas < this.#limite && this.#espera.length > 0) {
      const { tarefa, resolve, reject } = this.#espera.shift();
      this.#ativas += 1;
      // Promise.resolve().then captura também exceções síncronas da tarefa.
      Promise.resolve()
        .then(tarefa)
        .then(resolve, reject)
        .finally(() => {
          this.#ativas -= 1;
          this.#proxima();
          if (this.#ativas === 0 && this.#espera.length === 0) {
            this.#ociosos.splice(0).forEach((r) => r());
          }
        });
    }
  }
}

/** Executa `fn` sobre cada item respeitando o limite; mantém a ordem dos resultados. */
export function mapearComLimite(itens, limite, fn) {
  const fila = new FilaConcorrencia(limite);
  return Promise.all(Array.from(itens, (item, i) => fila.adicionar(() => fn(item, i))));
}
