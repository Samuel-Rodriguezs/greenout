// Trie (árvore de prefixos) para inserção, busca e autocompletar.

export class Trie {
  #raiz = { filhos: new Map(), fim: false };
  #total = 0;

  get tamanho() { return this.#total; }

  inserir(palavra) {
    let no = this.#raiz;
    for (const letra of palavra) {
      if (!no.filhos.has(letra)) no.filhos.set(letra, { filhos: new Map(), fim: false });
      no = no.filhos.get(letra);
    }
    if (!no.fim) {
      no.fim = true;
      this.#total += 1;
    }
    return this;
  }

  #buscarNo(texto) {
    let no = this.#raiz;
    for (const letra of texto) {
      no = no.filhos.get(letra);
      if (!no) return null;
    }
    return no;
  }

  contem(palavra) {
    return this.#buscarNo(palavra)?.fim === true;
  }

  temPrefixo(prefixo) {
    return this.#buscarNo(prefixo) !== null;
  }

  /** Todas as palavras com o prefixo, em ordem alfabética. */
  autocompletar(prefixo = '') {
    const no = this.#buscarNo(prefixo);
    if (!no) return [];
    const resultado = [];
    const percorrer = (atual, acumulado) => {
      if (atual.fim) resultado.push(acumulado);
      for (const letra of [...atual.filhos.keys()].sort()) {
        percorrer(atual.filhos.get(letra), acumulado + letra);
      }
    };
    percorrer(no, prefixo);
    return resultado;
  }

  remover(palavra) {
    const caminho = [];
    let no = this.#raiz;
    for (const letra of palavra) {
      const proximo = no.filhos.get(letra);
      if (!proximo) return false;
      caminho.push([no, letra]);
      no = proximo;
    }
    if (!no.fim) return false;
    no.fim = false;
    this.#total -= 1;
    // Poda nós que ficaram sem utilidade.
    for (let i = caminho.length - 1; i >= 0; i--) {
      const [pai, letra] = caminho[i];
      const filho = pai.filhos.get(letra);
      if (filho.fim || filho.filhos.size > 0) break;
      pai.filhos.delete(letra);
    }
    return true;
  }
}
