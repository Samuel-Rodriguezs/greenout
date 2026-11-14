// Autômato celular elementar 1D (regras de Wolfram, 0..255).

/** Retorna função (esq, centro, dir) -> 0|1 para o número de regra. */
export function regra(numero) {
  if (!Number.isInteger(numero) || numero < 0 || numero > 255) throw new Error('regra deve estar entre 0 e 255');
  return (e, c, d) => (numero >> (e * 4 + c * 2 + d)) & 1;
}

/** Próxima geração; `circular` conecta as bordas, senão fora = 0. */
export function proximaGeracao(celulas, numero, circular = true) {
  const f = regra(numero);
  const n = celulas.length;
  const ler = (i) => (circular ? celulas[(i + n) % n] : i < 0 || i >= n ? 0 : celulas[i]);
  return celulas.map((_, i) => f(ler(i - 1), ler(i), ler(i + 1)));
}

/** Gera `geracoes` linhas (inclui a inicial). */
export function simular(inicial, numero, geracoes, circular = true) {
  const hist = [inicial.slice()];
  for (let i = 1; i < geracoes; i++) hist.push(proximaGeracao(hist[i - 1], numero, circular));
  return hist;
}

/** Semente com uma única célula viva no centro. */
export function sementeCentral(largura) {
  const a = Array(largura).fill(0);
  a[Math.floor(largura / 2)] = 1;
  return a;
}

export function renderizar(historico, vivo = '#', morto = '.') {
  return historico.map((l) => l.map((v) => (v ? vivo : morto)).join('')).join('\n');
}
