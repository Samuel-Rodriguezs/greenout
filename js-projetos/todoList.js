// Lista de tarefas com filtros, ordenação por prioridade e serialização JSON.

const PRIORIDADES = { alta: 0, media: 1, baixa: 2 };

export class TodoList {
  #tarefas = [];
  #proximoId = 1;

  adicionar(titulo, { prioridade = 'media', vencimento = null } = {}) {
    if (typeof titulo !== 'string' || titulo.trim() === '') throw new Error('Título obrigatório');
    if (!(prioridade in PRIORIDADES)) throw new Error(`Prioridade inválida: ${prioridade}`);
    const tarefa = { id: this.#proximoId++, titulo: titulo.trim(), prioridade, vencimento, concluida: false };
    this.#tarefas.push(tarefa);
    return { ...tarefa };
  }

  #buscar(id) {
    const t = this.#tarefas.find((x) => x.id === id);
    if (!t) throw new Error(`Tarefa ${id} não encontrada`);
    return t;
  }

  concluir(id, concluida = true) {
    this.#buscar(id).concluida = concluida;
  }

  remover(id) {
    this.#buscar(id);
    this.#tarefas = this.#tarefas.filter((t) => t.id !== id);
  }

  editar(id, titulo) {
    if (!titulo?.trim()) throw new Error('Título obrigatório');
    this.#buscar(id).titulo = titulo.trim();
  }

  listar({ concluidas } = {}) {
    return this.#tarefas
      .filter((t) => concluidas === undefined || t.concluida === concluidas)
      .map((t) => ({ ...t }))
      .sort((a, b) => PRIORIDADES[a.prioridade] - PRIORIDADES[b.prioridade] || a.id - b.id);
  }

  atrasadas(hoje) {
    return this.listar({ concluidas: false }).filter((t) => t.vencimento && t.vencimento < hoje);
  }

  resumo() {
    const total = this.#tarefas.length;
    const feitas = this.#tarefas.filter((t) => t.concluida).length;
    return { total, feitas, pendentes: total - feitas, percentual: total ? Math.round((feitas / total) * 100) : 0 };
  }

  serializar() {
    return JSON.stringify({ versao: 1, proximoId: this.#proximoId, tarefas: this.#tarefas });
  }

  static desserializar(json) {
    let dados;
    try {
      dados = JSON.parse(json);
    } catch {
      throw new Error('JSON inválido');
    }
    if (dados?.versao !== 1 || !Array.isArray(dados.tarefas)) throw new Error('Formato não suportado');
    const lista = new TodoList();
    for (const t of dados.tarefas) {
      if (!(t.prioridade in PRIORIDADES) || typeof t.titulo !== 'string') throw new Error('Tarefa corrompida');
      lista.#tarefas.push({ ...t });
    }
    lista.#proximoId = dados.proximoId;
    return lista;
  }
}
