// Damas simples (8x8): captura obrigatória, promoção a dama, sem capturas em cadeia.
// Peças: 'b'/'B' brancas (sobem), 'p'/'P' pretas (descem); maiúscula = dama.

export function criarJogo() {
  const tab = Array.from({ length: 8 }, () => Array(8).fill(null));
  for (let l = 0; l < 8; l++) {
    for (let c = 0; c < 8; c++) {
      if ((l + c) % 2 === 0) continue; // só casas escuras
      if (l < 3) tab[l][c] = 'p';
      else if (l > 4) tab[l][c] = 'b';
    }
  }
  return { tabuleiro: tab, vez: 'b' };
}

export function criarDeTexto(linhas, vez = 'b') {
  const tab = linhas.map((s) => [...s].map((ch) => (ch === '.' ? null : ch)));
  if (tab.length !== 8 || tab.some((l) => l.length !== 8)) throw new Error('tabuleiro deve ser 8x8');
  return { tabuleiro: tab, vez };
}

function dono(peca) {
  return peca ? peca.toLowerCase() : null;
}

function direcoes(peca) {
  if (peca === peca.toUpperCase()) return [[-1, -1], [-1, 1], [1, -1], [1, 1]];
  return peca === 'b' ? [[-1, -1], [-1, 1]] : [[1, -1], [1, 1]];
}

const dentro = (l, c) => l >= 0 && l < 8 && c >= 0 && c < 8;

/** Lista de jogadas {de:[l,c], para:[l,c], captura:[l,c]|null}. Se houver captura, só elas. */
export function jogadasValidas(estado) {
  const { tabuleiro: t, vez } = estado;
  const simples = [];
  const capturas = [];
  for (let l = 0; l < 8; l++) {
    for (let c = 0; c < 8; c++) {
      const p = t[l][c];
      if (!p || dono(p) !== vez) continue;
      for (const [dl, dc] of direcoes(p)) {
        const a = l + dl;
        const b = c + dc;
        if (!dentro(a, b)) continue;
        if (t[a][b] === null) simples.push({ de: [l, c], para: [a, b], captura: null });
        else if (dono(t[a][b]) !== vez) {
          const x = a + dl;
          const y = b + dc;
          if (dentro(x, y) && t[x][y] === null) capturas.push({ de: [l, c], para: [x, y], captura: [a, b] });
        }
      }
    }
  }
  return capturas.length ? capturas : simples;
}

/** Aplica uma jogada válida e devolve novo estado. */
export function jogar(estado, de, para) {
  const jogada = jogadasValidas(estado).find((j) => j.de[0] === de[0] && j.de[1] === de[1] && j.para[0] === para[0] && j.para[1] === para[1]);
  if (!jogada) throw new Error('jogada inválida');
  const t = estado.tabuleiro.map((l) => l.slice());
  let peca = t[de[0]][de[1]];
  t[de[0]][de[1]] = null;
  if (jogada.captura) t[jogada.captura[0]][jogada.captura[1]] = null;
  if ((peca === 'b' && para[0] === 0) || (peca === 'p' && para[0] === 7)) peca = peca.toUpperCase();
  t[para[0]][para[1]] = peca;
  return { tabuleiro: t, vez: estado.vez === 'b' ? 'p' : 'b' };
}

/** 'b' | 'p' se alguém ganhou (adversário sem jogadas), senão null. */
export function vencedor(estado) {
  return jogadasValidas(estado).length === 0 ? (estado.vez === 'b' ? 'p' : 'b') : null;
}

export function contarPecas(estado) {
  const r = { b: 0, p: 0 };
  for (const linha of estado.tabuleiro) for (const p of linha) if (p) r[dono(p)]++;
  return r;
}
