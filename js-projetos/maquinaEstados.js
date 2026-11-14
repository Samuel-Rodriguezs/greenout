// Máquina de estados finitos com guardas, ações e histórico.

export class MaquinaEstados {
  #config;
  #estado;
  #historico = [];
  #ouvintes = new Set();

  // config: { inicial, estados: { nome: { on: { EVENTO: 'destino' | { alvo, guarda, acao } }, entrar, sair } } }
  constructor(config) {
    if (!config?.estados?.[config.inicial]) throw new Error('Estado inicial inválido');
    for (const [nome, def] of Object.entries(config.estados)) {
      for (const [evento, t] of Object.entries(def.on ?? {})) {
        const alvo = typeof t === 'string' ? t : t.alvo;
        if (!config.estados[alvo]) throw new Error(`Transição '${nome}' --${evento}--> '${alvo}' aponta para estado inexistente`);
      }
    }
    this.#config = config;
    this.#estado = config.inicial;
  }

  get estado() { return this.#estado; }
  get historico() { return [...this.#historico]; }

  pode(evento, contexto) {
    const t = this.#transicao(evento);
    return t !== undefined && (t.guarda?.(contexto) ?? true);
  }

  #transicao(evento) {
    const t = this.#config.estados[this.#estado].on?.[evento];
    return typeof t === 'string' ? { alvo: t } : t;
  }

  aoMudar(fn) {
    this.#ouvintes.add(fn);
    return () => this.#ouvintes.delete(fn);
  }

  enviar(evento, contexto) {
    const t = this.#transicao(evento);
    if (!t) throw new Error(`Evento '${evento}' inválido no estado '${this.#estado}'`);
    if (t.guarda && !t.guarda(contexto)) return false;
    const de = this.#estado;
    this.#config.estados[de].sair?.(contexto);
    t.acao?.(contexto);
    this.#estado = t.alvo;
    this.#config.estados[t.alvo].entrar?.(contexto);
    this.#historico.push({ de, evento, para: t.alvo });
    for (const fn of this.#ouvintes) fn(de, t.alvo, evento);
    return true;
  }

  estadoFinal() {
    return Object.keys(this.#config.estados[this.#estado].on ?? {}).length === 0;
  }
}

// Exemplo pronto: semáforo.
export function criarSemaforo() {
  return new MaquinaEstados({
    inicial: 'vermelho',
    estados: {
      vermelho: { on: { PROXIMO: 'verde' } },
      verde: { on: { PROXIMO: 'amarelo' } },
      amarelo: { on: { PROXIMO: 'vermelho' } },
    },
  });
}
