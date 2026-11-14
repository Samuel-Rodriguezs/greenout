// Jogo da velha com IA invencível via minimax com poda alfa-beta.
// Tabuleiro: array de 9 posições com 'X', 'O' ou null.

const LINHAS = [
  [0, 1, 2], [3, 4, 5], [6, 7, 8],
  [0, 3, 6], [1, 4, 7], [2, 5, 8],
  [0, 4, 8], [2, 4, 6],
];

export function novoTabuleiro() {
  return Array(9).fill(null);
}

export function vencedor(t) {
  for (const [a, b, c] of LINHAS) {
    if (t[a] && t[a] === t[b] && t[a] === t[c]) return t[a];
  }
  return null;
}

export function terminou(t) {
  return vencedor(t) !== null || t.every((c) => c !== null);
}

export function jogadasLivres(t) {
  return t.map((c, i) => (c === null ? i : -1)).filter((i) => i >= 0);
}

export function jogar(t, posicao, jogador) {
  if (!['X', 'O'].includes(jogador)) throw new Error('Jogador inválido');
  if (!Number.isInteger(posicao) || posicao < 0 || posicao > 8) throw new RangeError('Posição inválida');
  if (t[posicao] !== null) throw new Error('Posição ocupada');
  if (terminou(t)) throw new Error('Jogo encerrado');
  const novo = [...t];
  novo[posicao] = jogador;
  return novo;
}

const outro = (j) => (j === 'X' ? 'O' : 'X');

// Pontuação do ponto de vista de `eu`: positiva se eu venço (mais cedo é melhor).
function minimax(t, vez, eu, alfa, beta, profundidade) {
  const v = vencedor(t);
  if (v) return v === eu ? 10 - profundidade : profundidade - 10;
  const livres = jogadasLivres(t);
  if (livres.length === 0) return 0;
  const maximizando = vez === eu;
  let melhor = maximizando ? -Infinity : Infinity;
  for (const p of livres) {
    const nota = minimax(jogar(t, p, vez), outro(vez), eu, alfa, beta, profundidade + 1);
    if (maximizando) {
      melhor = Math.max(melhor, nota);
      alfa = Math.max(alfa, melhor);
    } else {
      melhor = Math.min(melhor, nota);
      beta = Math.min(beta, melhor);
    }
    if (beta <= alfa) break;
  }
  return melhor;
}

export function melhorJogada(t, jogador) {
  if (terminou(t)) throw new Error('Jogo encerrado');
  let melhor = null;
  let melhorNota = -Infinity;
  for (const p of jogadasLivres(t)) {
    const nota = minimax(jogar(t, p, jogador), outro(jogador), jogador, -Infinity, Infinity, 1);
    if (nota > melhorNota) {
      melhorNota = nota;
      melhor = p;
    }
  }
  return melhor;
}
