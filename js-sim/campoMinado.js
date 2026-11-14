// Campo minado com flood fill iterativo. Minas sorteadas no primeiro clique.

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

function vizinhos(jogo, l, c) {
  const r = [];
  for (let dl = -1; dl <= 1; dl++) {
    for (let dc = -1; dc <= 1; dc++) {
      if (!dl && !dc) continue;
      const a = l + dl;
      const b = c + dc;
      if (a >= 0 && b >= 0 && a < jogo.linhas && b < jogo.colunas) r.push([a, b]);
    }
  }
  return r;
}

function calcularNumeros(jogo) {
  for (let l = 0; l < jogo.linhas; l++) {
    for (let c = 0; c < jogo.colunas; c++) {
      jogo.numeros[l][c] = vizinhos(jogo, l, c).filter(([a, b]) => jogo.minas[a][b]).length;
    }
  }
}

function matriz(linhas, colunas, v) {
  return Array.from({ length: linhas }, () => Array(colunas).fill(v));
}

/** Jogo com minas a serem sorteadas no primeiro clique. */
export function criarJogo(linhas, colunas, numMinas, rng) {
  if (numMinas >= linhas * colunas) throw new Error('minas demais');
  return {
    linhas, colunas, numMinas, rng, minasColocadas: false,
    minas: matriz(linhas, colunas, false), numeros: matriz(linhas, colunas, 0),
    reveladas: matriz(linhas, colunas, false), bandeiras: matriz(linhas, colunas, false),
    status: 'jogando',
  };
}

/** Jogo com minas em posições conhecidas (útil para testes). */
export function criarComMinas(linhas, colunas, posicoes) {
  const jogo = criarJogo(linhas, colunas, posicoes.length, null);
  for (const [l, c] of posicoes) jogo.minas[l][c] = true;
  jogo.minasColocadas = true;
  calcularNumeros(jogo);
  return jogo;
}

function colocarMinas(jogo, seguroL, seguroC) {
  // zona segura 3x3; se não couber, protege só a célula clicada
  let proibidas = new Set([seguroL + ',' + seguroC, ...vizinhos(jogo, seguroL, seguroC).map(([a, b]) => a + ',' + b)]);
  if (jogo.linhas * jogo.colunas - proibidas.size < jogo.numMinas) proibidas = new Set([seguroL + ',' + seguroC]);
  const candidatas = [];
  for (let l = 0; l < jogo.linhas; l++) for (let c = 0; c < jogo.colunas; c++) if (!proibidas.has(l + ',' + c)) candidatas.push([l, c]);
  for (let i = candidatas.length - 1; i > 0; i--) {
    const j = Math.floor(jogo.rng() * (i + 1));
    [candidatas[i], candidatas[j]] = [candidatas[j], candidatas[i]];
  }
  for (const [l, c] of candidatas.slice(0, jogo.numMinas)) jogo.minas[l][c] = true;
  jogo.minasColocadas = true;
  calcularNumeros(jogo);
}

export function alternarBandeira(jogo, l, c) {
  if (jogo.status !== 'jogando' || jogo.reveladas[l][c]) return;
  jogo.bandeiras[l][c] = !jogo.bandeiras[l][c];
}

/** Revela célula; zeros expandem por flood fill. Retorna o status. */
export function revelar(jogo, l, c) {
  if (jogo.status !== 'jogando' || jogo.reveladas[l][c] || jogo.bandeiras[l][c]) return jogo.status;
  if (!jogo.minasColocadas) colocarMinas(jogo, l, c);
  if (jogo.minas[l][c]) {
    jogo.reveladas[l][c] = true;
    jogo.status = 'perdeu';
    return jogo.status;
  }
  const pilha = [[l, c]];
  while (pilha.length) {
    const [a, b] = pilha.pop();
    if (jogo.reveladas[a][b] || jogo.bandeiras[a][b]) continue;
    jogo.reveladas[a][b] = true;
    if (jogo.numeros[a][b] === 0) {
      for (const [x, y] of vizinhos(jogo, a, b)) if (!jogo.reveladas[x][y]) pilha.push([x, y]);
    }
  }
  const seguras = jogo.linhas * jogo.colunas - jogo.numMinas;
  const reveladas = jogo.reveladas.flat().filter(Boolean).length;
  if (reveladas === seguras) jogo.status = 'venceu';
  return jogo.status;
}

/** Representação textual: '#' oculta, 'F' bandeira, '.' zero, número, '*' mina. */
export function renderizar(jogo) {
  return jogo.reveladas.map((linha, l) => linha.map((rev, c) => {
    if (!rev) return jogo.bandeiras[l][c] ? 'F' : '#';
    if (jogo.minas[l][c]) return '*';
    return jogo.numeros[l][c] === 0 ? '.' : String(jogo.numeros[l][c]);
  }).join('')).join('\n');
}
