// Gerador de labirinto (DFS com backtracking, semente determinística) e solver BFS.
// Grade de células: cada célula tem paredes { N, S, L, O } (true = parede).

export function criarRandom(semente) {
  let s = semente >>> 0;
  return () => {
    // mulberry32
    s = (s + 0x6d2b79f5) >>> 0;
    let t = s;
    t = Math.imul(t ^ (t >>> 15), t | 1);
    t ^= t + Math.imul(t ^ (t >>> 7), t | 61);
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}

const DIRS = {
  N: { dl: -1, dc: 0, oposta: 'S' },
  S: { dl: 1, dc: 0, oposta: 'N' },
  L: { dl: 0, dc: 1, oposta: 'O' },
  O: { dl: 0, dc: -1, oposta: 'L' },
};

export function gerarLabirinto(linhas, colunas, semente = 1) {
  if (!Number.isInteger(linhas) || !Number.isInteger(colunas) || linhas < 1 || colunas < 1) {
    throw new RangeError('Dimensões inválidas');
  }
  const rand = criarRandom(semente);
  const celulas = Array.from({ length: linhas }, () =>
    Array.from({ length: colunas }, () => ({ N: true, S: true, L: true, O: true })),
  );
  const visitado = Array.from({ length: linhas }, () => Array(colunas).fill(false));
  const pilha = [[0, 0]];
  visitado[0][0] = true;

  while (pilha.length) {
    const [l, c] = pilha[pilha.length - 1];
    const opcoes = Object.entries(DIRS).filter(([, d]) => visitado[l + d.dl]?.[c + d.dc] === false);
    if (!opcoes.length) { pilha.pop(); continue; }
    const [nome, d] = opcoes[Math.floor(rand() * opcoes.length)];
    const [nl, nc] = [l + d.dl, c + d.dc];
    celulas[l][c][nome] = false;
    celulas[nl][nc][d.oposta] = false;
    visitado[nl][nc] = true;
    pilha.push([nl, nc]);
  }
  return { linhas, colunas, celulas };
}

export function resolver(lab, inicio = [0, 0], fim = [lab.linhas - 1, lab.colunas - 1]) {
  const dentro = ([l, c]) => l >= 0 && l < lab.linhas && c >= 0 && c < lab.colunas;
  if (!dentro(inicio) || !dentro(fim)) throw new RangeError('Ponto fora do labirinto');
  const chave = ([l, c]) => l * lab.colunas + c;
  const anterior = new Map([[chave(inicio), null]]);
  const fila = [inicio];
  for (let k = 0; k < fila.length; k++) {
    const [l, c] = fila[k];
    if (l === fim[0] && c === fim[1]) {
      const caminho = [];
      for (let atual = [l, c]; atual; atual = anterior.get(chave(atual))) caminho.push(atual);
      return caminho.reverse();
    }
    for (const [nome, d] of Object.entries(DIRS)) {
      const prox = [l + d.dl, c + d.dc];
      if (lab.celulas[l][c][nome] || !dentro(prox) || anterior.has(chave(prox))) continue;
      anterior.set(chave(prox), [l, c]);
      fila.push(prox);
    }
  }
  return null;
}

export function desenhar(lab, caminho = []) {
  const noCaminho = new Set(caminho.map(([l, c]) => `${l},${c}`));
  let s = '+' + '--+'.repeat(lab.colunas) + '\n';
  for (let l = 0; l < lab.linhas; l++) {
    let meio = '|';
    let baixo = '+';
    for (let c = 0; c < lab.colunas; c++) {
      const cel = lab.celulas[l][c];
      meio += (noCaminho.has(`${l},${c}`) ? '()' : '  ') + (cel.L ? '|' : ' ');
      baixo += (cel.S ? '--' : '  ') + '+';
    }
    s += meio + '\n' + baixo + '\n';
  }
  return s;
}
