// Simulador de fila de atendimento (FIFO, vários guichês), com chegadas e serviços exponenciais.

export function mulberry32(seed) {
  let a = seed >>> 0;
  return () => {
    a = (a + 0x6d2b79f5) >>> 0;
    let t = a;
    t = Math.imul(t ^ (t >>> 15), t | 1);
    t ^= t + Math.imul(t ^ (t >>> 7), t | 61);
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}

/** Amostra de distribuição exponencial com média `media`. */
export function exponencial(rng, media) {
  return -Math.log(1 - rng()) * media;
}

/** Gera clientes {id, chegada, servico} até `duracao`. */
export function gerarClientes(rng, { mediaChegada, mediaServico, duracao }) {
  const clientes = [];
  let t = exponencial(rng, mediaChegada);
  while (t <= duracao) {
    clientes.push({ id: clientes.length + 1, chegada: t, servico: exponencial(rng, mediaServico) });
    t += exponencial(rng, mediaChegada);
  }
  return clientes;
}

/** Simula clientes (ordenados por chegada) em `guiches` servidores. */
export function simularClientes(clientes, guiches) {
  if (!Number.isInteger(guiches) || guiches < 1) throw new Error('guichês deve ser inteiro >= 1');
  const livreEm = Array(guiches).fill(0);
  const ocupado = Array(guiches).fill(0);
  const atendimentos = [];
  for (const c of [...clientes].sort((a, b) => a.chegada - b.chegada || a.id - b.id)) {
    let g = 0;
    for (let i = 1; i < guiches; i++) if (livreEm[i] < livreEm[g]) g = i;
    const inicio = Math.max(c.chegada, livreEm[g]);
    const fim = inicio + c.servico;
    livreEm[g] = fim;
    ocupado[g] += c.servico;
    atendimentos.push({ id: c.id, guiche: g, chegada: c.chegada, inicio, fim, espera: inicio - c.chegada });
  }
  const n = atendimentos.length;
  const fimTotal = n ? Math.max(...atendimentos.map((a) => a.fim)) : 0;
  const esperas = atendimentos.map((a) => a.espera);
  return {
    atendimentos,
    atendidos: n,
    esperaMedia: n ? esperas.reduce((s, v) => s + v, 0) / n : 0,
    esperaMaxima: n ? Math.max(...esperas) : 0,
    tamanhoMaximoFila: tamanhoMaximoFila(atendimentos),
    tempoTotal: fimTotal,
    ocupacao: fimTotal > 0 ? ocupado.reduce((s, v) => s + v, 0) / (fimTotal * guiches) : 0,
  };
}

/** Maior número de clientes esperando (chegaram e ainda não iniciaram atendimento). */
export function tamanhoMaximoFila(atendimentos) {
  const eventos = [];
  for (const a of atendimentos) {
    if (a.espera > 0) {
      eventos.push([a.chegada, 1]);
      eventos.push([a.inicio, -1]);
    }
  }
  // saídas antes de entradas no mesmo instante
  eventos.sort((x, y) => x[0] - y[0] || x[1] - y[1]);
  let atual = 0;
  let max = 0;
  for (const [, d] of eventos) {
    atual += d;
    max = Math.max(max, atual);
  }
  return max;
}

export function simular(rng, config, guiches) {
  return simularClientes(gerarClientes(rng, config), guiches);
}
