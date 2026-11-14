// Problema da mochila 0/1 por programação dinâmica, com reconstrução dos itens.
// itens: [{ peso, valor }], capacidade inteira >= 0.
export function mochila(itens, capacidade) {
  if (!Number.isInteger(capacidade) || capacidade < 0) throw new RangeError('capacidade inválida');
  const n = itens.length;
  const dp = Array.from({ length: n + 1 }, () => new Array(capacidade + 1).fill(0));
  for (let i = 1; i <= n; i++) {
    const { peso, valor } = itens[i - 1];
    for (let c = 0; c <= capacidade; c++) {
      dp[i][c] = dp[i - 1][c];
      if (peso <= c) dp[i][c] = Math.max(dp[i][c], dp[i - 1][c - peso] + valor);
    }
  }
  const escolhidos = [];
  for (let i = n, c = capacidade; i > 0; i--) {
    if (dp[i][c] !== dp[i - 1][c]) { escolhidos.push(i - 1); c -= itens[i - 1].peso; }
  }
  return { valor: dp[n][capacidade], itens: escolhidos.reverse() };
}
