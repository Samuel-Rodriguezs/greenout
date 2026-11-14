// N-rainhas com backtracking e máscaras de bits.

// Gera todas as soluções: cada uma é um vetor col[linha] = coluna.
export function* solucoesRainhas(n) {
  if (!Number.isInteger(n) || n < 0) throw new RangeError('n inválido');
  const todas = (1 << n) - 1;
  const pos = [];
  function* colocar(linha, cols, d1, d2) {
    if (linha === n) { yield [...pos]; return; }
    let livres = todas & ~(cols | d1 | d2);
    while (livres) {
      const bit = livres & -livres;
      livres ^= bit;
      pos.push(31 - Math.clz32(bit));
      yield* colocar(linha + 1, cols | bit, ((d1 | bit) << 1) & todas, (d2 | bit) >> 1);
      pos.pop();
    }
  }
  yield* colocar(0, 0, 0, 0);
}

export function contarRainhas(n) {
  let c = 0;
  for (const _ of solucoesRainhas(n)) c++; // eslint-disable-line no-unused-vars
  return c;
}

export function primeiraSolucao(n) {
  const r = solucoesRainhas(n).next();
  return r.done ? null : r.value;
}

// Desenha o tabuleiro: 'R' rainha, '.' vazio.
export function desenhar(solucao) {
  return solucao.map((c) => '.'.repeat(c) + 'R' + '.'.repeat(solucao.length - c - 1)).join('\n');
}
