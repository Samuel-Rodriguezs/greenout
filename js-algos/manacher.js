// Algoritmo de Manacher: palíndromos em tempo linear.

// Raios sobre a string transformada "^#a#b#$". p[i] = tamanho do palíndromo centrado em i.
function raios(s) {
  const t = ['^', '#'];
  for (const c of s) t.push(c, '#');
  t.push('$');
  const p = new Array(t.length).fill(0);
  let centro = 0, direita = 0;
  for (let i = 1; i < t.length - 1; i++) {
    if (i < direita) p[i] = Math.min(direita - i, p[2 * centro - i]);
    while (t[i + 1 + p[i]] === t[i - 1 - p[i]]) p[i]++;
    if (i + p[i] > direita) { centro = i; direita = i + p[i]; }
  }
  return p;
}

// Maior substring palindrômica (a mais à esquerda em caso de empate).
export function maiorPalindromo(s) {
  if (s.length === 0) return '';
  const p = raios(s);
  let melhor = 0, c = 0;
  for (let i = 1; i < p.length - 1; i++) if (p[i] > melhor) { melhor = p[i]; c = i; }
  const ini = (c - melhor) >> 1;
  return s.slice(ini, ini + melhor);
}

// Quantidade de substrings palindrômicas (por posição).
export function contarPalindromos(s) {
  if (s.length === 0) return 0;
  return raios(s).reduce((soma, r) => soma + ((r + 1) >> 1), 0);
}

export function ehPalindromo(s) {
  return maiorPalindromo(s).length === s.length;
}
