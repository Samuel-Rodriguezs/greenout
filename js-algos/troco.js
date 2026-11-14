// Problema do troco por programação dinâmica (moedas ilimitadas).

// Menor número de moedas para formar valor; null se impossível. Também devolve as moedas.
export function menorTroco(moedas, valor) {
  if (!Number.isInteger(valor) || valor < 0) throw new RangeError('valor inválido');
  const dp = new Array(valor + 1).fill(Infinity);
  const usada = new Array(valor + 1).fill(0);
  dp[0] = 0;
  for (let v = 1; v <= valor; v++) {
    for (const m of moedas) {
      if (m > 0 && m <= v && dp[v - m] + 1 < dp[v]) { dp[v] = dp[v - m] + 1; usada[v] = m; }
    }
  }
  if (dp[valor] === Infinity) return null;
  const lista = [];
  for (let v = valor; v > 0; v -= usada[v]) lista.push(usada[v]);
  return { quantidade: dp[valor], moedas: lista.sort((a, b) => b - a) };
}

// Número de combinações distintas (ordem não importa) que somam valor.
export function formasDeTroco(moedas, valor) {
  const dp = new Array(valor + 1).fill(0n);
  dp[0] = 1n;
  for (const m of moedas) {
    for (let v = m; v <= valor; v++) dp[v] += dp[v - m];
  }
  return dp[valor];
}
