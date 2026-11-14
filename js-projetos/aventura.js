// Motor de aventura de texto: salas, saídas, itens, portas trancadas e comandos em português.

export class Aventura {
  #mapa;
  #sala;
  #inventario = new Set();
  #itensNasSalas = new Map();
  #desbloqueadas = new Set();
  #movimentos = 0;

  // mapa: { sala: { descricao, saidas: { norte: 'outra' }, itens: [..], trancadas: { norte: 'chave' } } }
  constructor(mapa, inicial) {
    if (!mapa[inicial]) throw new Error('Sala inicial inexistente');
    for (const [nome, s] of Object.entries(mapa)) {
      for (const destino of Object.values(s.saidas ?? {})) {
        if (!mapa[destino]) throw new Error(`Sala '${nome}' leva a '${destino}', que não existe`);
      }
      this.#itensNasSalas.set(nome, new Set(s.itens ?? []));
    }
    this.#mapa = mapa;
    this.#sala = inicial;
  }

  get sala() { return this.#sala; }
  get inventario() { return [...this.#inventario].sort(); }
  get movimentos() { return this.#movimentos; }

  descrever() {
    const s = this.#mapa[this.#sala];
    const itens = [...this.#itensNasSalas.get(this.#sala)];
    const saidas = Object.keys(s.saidas ?? {});
    let t = s.descricao;
    if (itens.length) t += ` Você vê: ${itens.join(', ')}.`;
    t += saidas.length ? ` Saídas: ${saidas.join(', ')}.` : ' Não há saídas.';
    return t;
  }

  ir(direcao) {
    const s = this.#mapa[this.#sala];
    const destino = s.saidas?.[direcao];
    if (!destino) return `Você não pode ir para ${direcao}.`;
    const chave = s.trancadas?.[direcao];
    if (chave && !this.#desbloqueadas.has(`${this.#sala}:${direcao}`)) {
      if (!this.#inventario.has(chave)) return `A passagem ao ${direcao} está trancada.`;
      this.#desbloqueadas.add(`${this.#sala}:${direcao}`);
    }
    this.#sala = destino;
    this.#movimentos++;
    return this.descrever();
  }

  pegar(item) {
    const itens = this.#itensNasSalas.get(this.#sala);
    if (!itens.delete(item)) return `Não há ${item} aqui.`;
    this.#inventario.add(item);
    return `Você pegou ${item}.`;
  }

  largar(item) {
    if (!this.#inventario.delete(item)) return `Você não possui ${item}.`;
    this.#itensNasSalas.get(this.#sala).add(item);
    return `Você largou ${item}.`;
  }

  executar(comando) {
    const [verbo, ...resto] = comando.trim().toLowerCase().split(/\s+/);
    const alvo = resto.join(' ');
    switch (verbo) {
      case 'olhar': return this.descrever();
      case 'ir': return alvo ? this.ir(alvo) : 'Ir para onde?';
      case 'pegar': return alvo ? this.pegar(alvo) : 'Pegar o quê?';
      case 'largar': return alvo ? this.largar(alvo) : 'Largar o quê?';
      case 'inventario': return this.inventario.length ? `Você carrega: ${this.inventario.join(', ')}.` : 'Você não carrega nada.';
      default: return `Não entendi '${comando.trim()}'.`;
    }
  }

  venceu(salaFinal) {
    return this.#sala === salaFinal;
  }
}
