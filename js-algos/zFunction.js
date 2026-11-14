// Algoritmo Z: z[i] = tamanho do maior prefixo de s que começa em i.
export function zFunction(s) {
  const n = s.length;
  const z = new Array(n).fill(0);
  if (n > 0) z[0] = n;
  for (let i = 1, l = 0, r = 0; i < n; i++) {
    if (i < r) z[i] = Math.min(r - i, z[i - l]);
    while (i + z[i] < n && s[z[i]] === s[i + z[i]]) z[i]++;
    if (i + z[i] > r) { l = i; r = i + z[i]; }
  }
  return z;
}

// Posições de padrao em texto usando Z sobre padrao + sentinela + texto.
export function buscaZ(texto, padrao) {
  if (padrao.length === 0) return [];
  const sentinela = '\u0000';
  const z = zFunction(padrao + sentinela + texto);
  const achados = [];
  for (let i = padrao.length + 1; i < z.length; i++) {
    if (z[i] === padrao.length) achados.push(i - padrao.length - 1);
  }
  return achados;
}
