// Batalha naval: posicionamento aleatório da frota e tiros.

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

export const FROTA_PADRAO = [5, 4, 3, 3, 2];

/** Cria tabuleiro com navios dados: [{celulas:[[l,c],...]}]. */
export function criarComNavios(tamanho, navios) {
  const ocupadas = new Set();
  for (const n of navios) {
    for (const [l, c] of n.celulas) {
      if (l < 0 || c < 0 || l >= tamanho || c >= tamanho) throw new Error('navio fora do tabuleiro');
      const k = l + ',' + c;
      if (ocupadas.has(k)) throw new Error('navios sobrepostos');
      ocupadas.add(k);
    }
  }
  return {
    tamanho,
    navios: navios.map((n) => ({ celulas: n.celulas.map(([l, c]) => [l, c]), acertos: new Set() })),
    tiros: new Set(),
  };
}

/** Posiciona a frota aleatoriamente sem sobreposição. */
export function criarAleatorio(rng, tamanho = 10, frota = FROTA_PADRAO) {
  const ocupadas = new Set();
  const navios = [];
  for (const tam of frota) {
    let colocado = false;
    for (let tentativa = 0; tentativa < 1000 && !colocado; tentativa++) {
      const horizontal = rng() < 0.5;
      const l = Math.floor(rng() * (horizontal ? tamanho : tamanho - tam + 1));
      const c = Math.floor(rng() * (horizontal ? tamanho - tam + 1 : tamanho));
      const celulas = [];
      for (let i = 0; i < tam; i++) celulas.push(horizontal ? [l, c + i] : [l + i, c]);
      if (celulas.some(([a, b]) => ocupadas.has(a + ',' + b))) continue;
      celulas.forEach(([a, b]) => ocupadas.add(a + ',' + b));
      navios.push({ celulas });
      colocado = true;
    }
    if (!colocado) throw new Error('não foi possível posicionar a frota');
  }
  return criarComNavios(tamanho, navios);
}

/** Atira em (l,c): 'agua' | 'acerto' | 'afundou' | 'repetido'. */
export function atirar(jogo, l, c) {
  if (l < 0 || c < 0 || l >= jogo.tamanho || c >= jogo.tamanho) throw new Error('tiro fora do tabuleiro');
  const k = l + ',' + c;
  if (jogo.tiros.has(k)) return 'repetido';
  jogo.tiros.add(k);
  for (const n of jogo.navios) {
    if (n.celulas.some(([a, b]) => a === l && b === c)) {
      n.acertos.add(k);
      return n.acertos.size === n.celulas.length ? 'afundou' : 'acerto';
    }
  }
  return 'agua';
}

export function venceu(jogo) {
  return jogo.navios.every((n) => n.acertos.size === n.celulas.length);
}

export function naviosRestantes(jogo) {
  return jogo.navios.filter((n) => n.acertos.size < n.celulas.length).length;
}
