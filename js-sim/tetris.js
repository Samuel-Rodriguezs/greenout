// Tetris: colisão, rotação, fixação e limpeza de linhas. Sacola de 7 peças via PRNG.

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

export const PECAS = {
  I: [[0, 0, 0, 0], [1, 1, 1, 1], [0, 0, 0, 0], [0, 0, 0, 0]],
  O: [[1, 1], [1, 1]],
  T: [[0, 1, 0], [1, 1, 1], [0, 0, 0]],
  S: [[0, 1, 1], [1, 1, 0], [0, 0, 0]],
  Z: [[1, 1, 0], [0, 1, 1], [0, 0, 0]],
  J: [[1, 0, 0], [1, 1, 1], [0, 0, 0]],
  L: [[0, 0, 1], [1, 1, 1], [0, 0, 0]],
};
const PONTOS_LINHAS = [0, 100, 300, 500, 800];

/** Rotação horária de matriz quadrada. */
export function rotacionar(m) {
  const n = m.length;
  return m.map((_, l) => m.map((__, c) => m[n - 1 - c][l]));
}

export function criarTabuleiro(largura = 10, altura = 20) {
  return Array.from({ length: altura }, () => Array(largura).fill(0));
}

/** Verdadeiro se a forma na posição (x,y) sai do tabuleiro ou bate em bloco fixo. */
export function colide(tabuleiro, forma, x, y) {
  for (let l = 0; l < forma.length; l++) {
    for (let c = 0; c < forma[l].length; c++) {
      if (!forma[l][c]) continue;
      const tl = y + l;
      const tc = x + c;
      if (tc < 0 || tc >= tabuleiro[0].length || tl >= tabuleiro.length) return true;
      if (tl >= 0 && tabuleiro[tl][tc]) return true;
    }
  }
  return false;
}

export function fixar(tabuleiro, forma, x, y, tipo = 1) {
  const novo = tabuleiro.map((l) => l.slice());
  forma.forEach((linha, l) => linha.forEach((v, c) => {
    if (v && y + l >= 0) novo[y + l][x + c] = tipo;
  }));
  return novo;
}

export function limparLinhas(tabuleiro) {
  const restantes = tabuleiro.filter((l) => !l.every(Boolean));
  const removidas = tabuleiro.length - restantes.length;
  const vazias = Array.from({ length: removidas }, () => Array(tabuleiro[0].length).fill(0));
  return { tabuleiro: [...vazias, ...restantes], linhas: removidas };
}

function embaralhar(arr, rng) {
  const a = arr.slice();
  for (let i = a.length - 1; i > 0; i--) {
    const j = Math.floor(rng() * (i + 1));
    [a[i], a[j]] = [a[j], a[i]];
  }
  return a;
}

function proximaDaSacola(estado, rng) {
  let sacola = estado.sacola;
  if (sacola.length === 0) sacola = embaralhar(Object.keys(PECAS), rng);
  const [tipo, ...resto] = sacola;
  return { tipo, sacola: resto };
}

function gerarPeca(estado, rng) {
  const { tipo, sacola } = proximaDaSacola(estado, rng);
  const forma = PECAS[tipo];
  const peca = { tipo, forma, x: Math.floor((estado.tabuleiro[0].length - forma[0].length) / 2), y: 0 };
  const fim = colide(estado.tabuleiro, forma, peca.x, peca.y);
  return { ...estado, sacola, peca, fimDeJogo: fim };
}

export function criarJogo(rng, largura = 10, altura = 20) {
  return gerarPeca({ tabuleiro: criarTabuleiro(largura, altura), sacola: [], peca: null, pontos: 0, linhas: 0, fimDeJogo: false }, rng);
}

export function moverLateral(estado, dx) {
  if (estado.fimDeJogo) return estado;
  const { peca } = estado;
  if (colide(estado.tabuleiro, peca.forma, peca.x + dx, peca.y)) return estado;
  return { ...estado, peca: { ...peca, x: peca.x + dx } };
}

/** Rotação horária com "wall kick" simples (tenta deslocar 1 ou 2 colunas). */
export function girar(estado) {
  if (estado.fimDeJogo) return estado;
  const { peca } = estado;
  const forma = rotacionar(peca.forma);
  for (const dx of [0, -1, 1, -2, 2]) {
    if (!colide(estado.tabuleiro, forma, peca.x + dx, peca.y)) {
      return { ...estado, peca: { ...peca, forma, x: peca.x + dx } };
    }
  }
  return estado;
}

/** Gravidade: desce uma linha; se não der, fixa, limpa linhas e gera a próxima peça. */
export function descer(estado, rng) {
  if (estado.fimDeJogo) return estado;
  const { peca } = estado;
  if (!colide(estado.tabuleiro, peca.forma, peca.x, peca.y + 1)) {
    return { ...estado, peca: { ...peca, y: peca.y + 1 } };
  }
  const fixado = fixar(estado.tabuleiro, peca.forma, peca.x, peca.y, peca.tipo);
  const { tabuleiro, linhas } = limparLinhas(fixado);
  return gerarPeca({
    ...estado, tabuleiro, linhas: estado.linhas + linhas,
    pontos: estado.pontos + PONTOS_LINHAS[linhas],
  }, rng);
}

/** Queda direta até o fim. */
export function quedaDireta(estado, rng) {
  if (estado.fimDeJogo) return estado;
  let y = estado.peca.y;
  while (!colide(estado.tabuleiro, estado.peca.forma, estado.peca.x, y + 1)) y++;
  return descer({ ...estado, peca: { ...estado.peca, y } }, rng);
}
