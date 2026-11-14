// Conecta 4 com minimax + poda alfa-beta. Jogadores: 1 e 2; vazio = 0.

export const LINHAS = 6;
export const COLUNAS = 7;

export function criarTabuleiro() {
  return Array.from({ length: LINHAS }, () => Array(COLUNAS).fill(0));
}

export function colunaLivre(tab, c) {
  return tab[0][c] === 0;
}

export function colunasValidas(tab) {
  // ordem do centro para as bordas melhora a poda
  return [3, 2, 4, 1, 5, 0, 6].filter((c) => colunaLivre(tab, c));
}

/** Solta a peça na coluna e devolve novo tabuleiro. */
export function jogar(tab, coluna, jogador) {
  if (coluna < 0 || coluna >= COLUNAS || !colunaLivre(tab, coluna)) throw new Error('coluna inválida');
  const novo = tab.map((l) => l.slice());
  for (let l = LINHAS - 1; l >= 0; l--) {
    if (novo[l][coluna] === 0) {
      novo[l][coluna] = jogador;
      return novo;
    }
  }
  return novo;
}

const DIRECOES = [[0, 1], [1, 0], [1, 1], [1, -1]];

/** Retorna 1, 2, ou 0 se ninguém ganhou. */
export function vencedor(tab) {
  for (let l = 0; l < LINHAS; l++) {
    for (let c = 0; c < COLUNAS; c++) {
      const v = tab[l][c];
      if (!v) continue;
      for (const [dl, dc] of DIRECOES) {
        let k = 1;
        while (k < 4) {
          const a = l + dl * k;
          const b = c + dc * k;
          if (a < 0 || a >= LINHAS || b < 0 || b >= COLUNAS || tab[a][b] !== v) break;
          k++;
        }
        if (k === 4) return v;
      }
    }
  }
  return 0;
}

export function empate(tab) {
  return vencedor(tab) === 0 && colunasValidas(tab).length === 0;
}

function pontuarJanela(janela, jogador) {
  const adv = jogador === 1 ? 2 : 1;
  const meus = janela.filter((v) => v === jogador).length;
  const deles = janela.filter((v) => v === adv).length;
  const vazios = 4 - meus - deles;
  if (meus && deles) return 0;
  if (meus === 3 && vazios === 1) return 5;
  if (meus === 2 && vazios === 2) return 2;
  if (deles === 3 && vazios === 1) return -4;
  return 0;
}

/** Heurística estática do ponto de vista de `jogador`. */
export function avaliar(tab, jogador) {
  let pontos = 0;
  for (let l = 0; l < LINHAS; l++) if (tab[l][3] === jogador) pontos += 3;
  for (let l = 0; l < LINHAS; l++) {
    for (let c = 0; c < COLUNAS; c++) {
      for (const [dl, dc] of DIRECOES) {
        const fl = l + dl * 3;
        const fc = c + dc * 3;
        if (fl < 0 || fl >= LINHAS || fc < 0 || fc >= COLUNAS) continue;
        const janela = [0, 1, 2, 3].map((k) => tab[l + dl * k][c + dc * k]);
        pontos += pontuarJanela(janela, jogador);
      }
    }
  }
  return pontos;
}

const VITORIA = 1_000_000;

function minimax(tab, prof, alfa, beta, maximizando, eu, vez) {
  const v = vencedor(tab);
  if (v === eu) return VITORIA + prof; // vitória mais cedo vale mais
  if (v !== 0) return -VITORIA - prof;
  const cols = colunasValidas(tab);
  if (cols.length === 0) return 0;
  if (prof === 0) return avaliar(tab, eu);
  const prox = vez === 1 ? 2 : 1;
  if (maximizando) {
    let melhor = -Infinity;
    for (const c of cols) {
      melhor = Math.max(melhor, minimax(jogar(tab, c, vez), prof - 1, alfa, beta, false, eu, prox));
      alfa = Math.max(alfa, melhor);
      if (alfa >= beta) break;
    }
    return melhor;
  }
  let melhor = Infinity;
  for (const c of cols) {
    melhor = Math.min(melhor, minimax(jogar(tab, c, vez), prof - 1, alfa, beta, true, eu, prox));
    beta = Math.min(beta, melhor);
    if (alfa >= beta) break;
  }
  return melhor;
}

/** Melhor coluna para `jogador` com busca de profundidade `prof`. Desempate: centro primeiro. */
export function melhorJogada(tab, jogador, prof = 4) {
  const cols = colunasValidas(tab);
  if (cols.length === 0) return null;
  const adv = jogador === 1 ? 2 : 1;
  let melhorCol = cols[0];
  let melhorValor = -Infinity;
  for (const c of cols) {
    const valor = minimax(jogar(tab, c, jogador), prof - 1, -Infinity, Infinity, false, jogador, adv);
    if (valor > melhorValor) {
      melhorValor = valor;
      melhorCol = c;
    }
  }
  return melhorCol;
}
