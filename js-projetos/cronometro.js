// Cronômetro e contagem regressiva baseados em setInterval/Date.now (testáveis com mock.timers).

export function formatarTempo(ms) {
  const total = Math.floor(ms / 1000);
  const h = String(Math.floor(total / 3600)).padStart(2, '0');
  const m = String(Math.floor((total % 3600) / 60)).padStart(2, '0');
  const s = String(total % 60).padStart(2, '0');
  return `${h}:${m}:${s}`;
}

export class Cronometro {
  #acumulado = 0;
  #inicio = null;
  #voltas = [];
  #intervalo = null;
  #aoTick;

  constructor({ aoTick = () => {}, passoMs = 1000 } = {}) {
    this.#aoTick = aoTick;
    this.passoMs = passoMs;
  }

  get rodando() { return this.#inicio !== null; }

  get decorrido() {
    return this.#acumulado + (this.#inicio === null ? 0 : Date.now() - this.#inicio);
  }

  iniciar() {
    if (this.rodando) throw new Error('Cronômetro já está rodando');
    this.#inicio = Date.now();
    this.#intervalo = setInterval(() => this.#aoTick(this.decorrido), this.passoMs);
  }

  pausar() {
    if (!this.rodando) throw new Error('Cronômetro não está rodando');
    this.#acumulado = this.decorrido;
    this.#inicio = null;
    clearInterval(this.#intervalo);
    this.#intervalo = null;
  }

  volta() {
    const atual = this.decorrido;
    const anterior = this.#voltas.length ? this.#voltas.at(-1).total : 0;
    const v = { numero: this.#voltas.length + 1, total: atual, parcial: atual - anterior };
    this.#voltas.push(v);
    return v;
  }

  get voltas() { return [...this.#voltas]; }

  zerar() {
    if (this.rodando) this.pausar();
    this.#acumulado = 0;
    this.#voltas = [];
  }
}

// Contagem regressiva: chama aoTick(restanteMs) a cada passo e aoFim() ao zerar.
export function contagemRegressiva(duracaoMs, { aoTick = () => {}, aoFim = () => {}, passoMs = 1000 } = {}) {
  if (!(duracaoMs > 0)) throw new RangeError('Duração deve ser positiva');
  const fim = Date.now() + duracaoMs;
  const id = setInterval(() => {
    const restante = Math.max(0, fim - Date.now());
    aoTick(restante);
    if (restante === 0) {
      clearInterval(id);
      aoFim();
    }
  }, passoMs);
  return () => clearInterval(id);
}
