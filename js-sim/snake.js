// Snake: estado imutável, comida posicionada via PRNG injetável.

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

const VETORES = { cima: { x: 0, y: -1 }, baixo: { x: 0, y: 1 }, esquerda: { x: -1, y: 0 }, direita: { x: 1, y: 0 } };
const OPOSTA = { cima: 'baixo', baixo: 'cima', esquerda: 'direita', direita: 'esquerda' };

export function posicionarComida(largura, altura, cobra, rng) {
  const ocupadas = new Set(cobra.map((p) => p.x + ',' + p.y));
  const livres = [];
  for (let y = 0; y < altura; y++) for (let x = 0; x < largura; x++) if (!ocupadas.has(x + ',' + y)) livres.push({ x, y });
  if (livres.length === 0) return null;
  return livres[Math.floor(rng() * livres.length)];
}

export function criarJogo(largura, altura, rng) {
  const cx = Math.floor(largura / 2);
  const cy = Math.floor(altura / 2);
  const cobra = [{ x: cx, y: cy }, { x: cx - 1, y: cy }, { x: cx - 2, y: cy }];
  return {
    largura, altura, cobra, direcao: 'direita', pontos: 0, vivo: true,
    comida: posicionarComida(largura, altura, cobra, rng),
  };
}

/** Muda a direção, ignorando inversão de 180 graus. */
export function virar(estado, direcao) {
  if (!VETORES[direcao]) throw new Error('direção inválida');
  if (OPOSTA[direcao] === estado.direcao) return estado;
  return { ...estado, direcao };
}

/** Avança um passo. */
export function passo(estado, rng) {
  if (!estado.vivo) return estado;
  const v = VETORES[estado.direcao];
  const cabeca = { x: estado.cobra[0].x + v.x, y: estado.cobra[0].y + v.y };
  const comeu = estado.comida && cabeca.x === estado.comida.x && cabeca.y === estado.comida.y;
  // a cauda libera sua casa, exceto se a cobra cresce
  const corpo = comeu ? estado.cobra : estado.cobra.slice(0, -1);
  const bateuParede = cabeca.x < 0 || cabeca.y < 0 || cabeca.x >= estado.largura || cabeca.y >= estado.altura;
  const bateuCorpo = corpo.some((p) => p.x === cabeca.x && p.y === cabeca.y);
  if (bateuParede || bateuCorpo) return { ...estado, vivo: false };
  const cobra = [cabeca, ...corpo];
  if (!comeu) return { ...estado, cobra };
  return {
    ...estado, cobra, pontos: estado.pontos + 1,
    comida: posicionarComida(estado.largura, estado.altura, cobra, rng),
  };
}
