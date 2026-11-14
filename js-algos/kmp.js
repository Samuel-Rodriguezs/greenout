// Knuth-Morris-Pratt: busca de padrão em O(n + m).

// Tabela de falhas (maior prefixo que também é sufixo).
export function tabelaPrefixo(p) {
  const pi = new Array(p.length).fill(0);
  for (let i = 1, k = 0; i < p.length; i++) {
    while (k > 0 && p[i] !== p[k]) k = pi[k - 1];
    if (p[i] === p[k]) k++;
    pi[i] = k;
  }
  return pi;
}

// Todas as posições (inclusive sobrepostas) onde padrao ocorre em texto.
export function kmp(texto, padrao) {
  if (padrao.length === 0) return [];
  const pi = tabelaPrefixo(padrao);
  const achados = [];
  for (let i = 0, k = 0; i < texto.length; i++) {
    while (k > 0 && texto[i] !== padrao[k]) k = pi[k - 1];
    if (texto[i] === padrao[k]) k++;
    if (k === padrao.length) { achados.push(i - k + 1); k = pi[k - 1]; }
  }
  return achados;
}
