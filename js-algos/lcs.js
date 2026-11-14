// Maior subsequência comum (LCS) por programação dinâmica.
export function lcs(a, b) {
  const n = a.length, m = b.length;
  const dp = Array.from({ length: n + 1 }, () => new Array(m + 1).fill(0));
  for (let i = 1; i <= n; i++) {
    for (let j = 1; j <= m; j++) {
      dp[i][j] = a[i - 1] === b[j - 1] ? dp[i - 1][j - 1] + 1 : Math.max(dp[i - 1][j], dp[i][j - 1]);
    }
  }
  let i = n, j = m;
  const saida = [];
  while (i > 0 && j > 0) {
    if (a[i - 1] === b[j - 1]) { saida.push(a[i - 1]); i--; j--; }
    else if (dp[i - 1][j] >= dp[i][j - 1]) i--;
    else j--;
  }
  saida.reverse();
  return typeof a === 'string' ? saida.join('') : saida;
}

export const tamanhoLcs = (a, b) => lcs(a, b).length;
