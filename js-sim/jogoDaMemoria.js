// Jogo da memória: cartas embaralhadas via PRNG injetável.

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

export function embaralhar(lista, rng) {
  const a = lista.slice();
  for (let i = a.length - 1; i > 0; i--) {
    const j = Math.floor(rng() * (i + 1));
    [a[i], a[j]] = [a[j], a[i]];
  }
  return a;
}

/** valores: lista de símbolos distintos; cada um vira um par. */
export function criarJogo(valores, rng) {
  if (new Set(valores).size !== valores.length) throw new Error('valores devem ser distintos');
  const cartas = embaralhar([...valores, ...valores], rng).map((valor) => ({ valor, estado: 'oculta' }));
  return { cartas, viradas: [], tentativas: 0, status: 'jogando' };
}

/**
 * Vira a carta i. Duas viradas que não combinam permanecem visíveis até a
 * próxima jogada, quando são ocultadas automaticamente.
 */
export function virar(jogo, i) {
  if (jogo.status !== 'jogando') return jogo;
  if (i < 0 || i >= jogo.cartas.length) throw new Error('índice inválido');
  let cartas = jogo.cartas.slice();
  let viradas = jogo.viradas;
  if (viradas.length === 2) {
    // erro anterior: esconde as duas
    viradas.forEach((k) => { cartas[k] = { ...cartas[k], estado: 'oculta' }; });
    viradas = [];
  }
  if (cartas[i].estado !== 'oculta') return { ...jogo, cartas, viradas };
  cartas[i] = { ...cartas[i], estado: 'virada' };
  viradas = [...viradas, i];
  let tentativas = jogo.tentativas;
  if (viradas.length === 2) {
    tentativas++;
    const [a, b] = viradas;
    if (cartas[a].valor === cartas[b].valor) {
      cartas[a] = { ...cartas[a], estado: 'par' };
      cartas[b] = { ...cartas[b], estado: 'par' };
      viradas = [];
    }
  }
  const status = cartas.every((c) => c.estado === 'par') ? 'venceu' : 'jogando';
  return { cartas, viradas, tentativas, status };
}
