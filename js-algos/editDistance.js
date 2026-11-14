// Distância de edição (Levenshtein) com memória O(min(n, m)) e script de operações.
export function distanciaEdicao(a, b) {
  if (a.length < b.length) [a, b] = [b, a];
  let ant = Array.from({ length: b.length + 1 }, (_, j) => j);
  for (let i = 1; i <= a.length; i++) {
    const atual = [i];
    for (let j = 1; j <= b.length; j++) {
      const custo = a[i - 1] === b[j - 1] ? 0 : 1;
      atual[j] = Math.min(ant[j] + 1, atual[j - 1] + 1, ant[j - 1] + custo);
    }
    ant = atual;
  }
  return ant[b.length];
}

// Operações para transformar a em b: 'manter', 'trocar', 'inserir', 'remover'.
export function operacoesEdicao(a, b) {
  const n = a.length, m = b.length;
  const dp = Array.from({ length: n + 1 }, (_, i) => [i, ...new Array(m).fill(0)]);
  for (let j = 0; j <= m; j++) dp[0][j] = j;
  for (let i = 1; i <= n; i++) {
    for (let j = 1; j <= m; j++) {
      dp[i][j] = Math.min(dp[i - 1][j] + 1, dp[i][j - 1] + 1, dp[i - 1][j - 1] + (a[i - 1] === b[j - 1] ? 0 : 1));
    }
  }
  const ops = [];
  let i = n, j = m;
  while (i > 0 || j > 0) {
    if (i > 0 && j > 0 && a[i - 1] === b[j - 1] && dp[i][j] === dp[i - 1][j - 1]) {
      ops.push({ op: 'manter', char: a[i - 1] }); i--; j--;
    } else if (i > 0 && j > 0 && dp[i][j] === dp[i - 1][j - 1] + 1) {
      ops.push({ op: 'trocar', de: a[i - 1], para: b[j - 1] }); i--; j--;
    } else if (j > 0 && dp[i][j] === dp[i][j - 1] + 1) {
      ops.push({ op: 'inserir', char: b[j - 1] }); j--;
    } else {
      ops.push({ op: 'remover', char: a[i - 1] }); i--;
    }
  }
  return ops.reverse();
}
