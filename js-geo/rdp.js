// Simplificação de linha de Ramer-Douglas-Peucker (iterativa, sem recursão).

/** Distância de p ao segmento a-b. */
export function distanciaPontoSegmento(p, a, b) {
  const dx = b[0] - a[0], dy = b[1] - a[1];
  const l2 = dx * dx + dy * dy;
  if (l2 === 0) return Math.hypot(p[0] - a[0], p[1] - a[1]);
  const t = Math.max(0, Math.min(1, ((p[0] - a[0]) * dx + (p[1] - a[1]) * dy) / l2));
  return Math.hypot(p[0] - (a[0] + t * dx), p[1] - (a[1] + t * dy));
}

/**
 * Mantém os pontos que desviam mais que `tolerancia` da reta entre os
 * extremos de cada trecho. Extremos sempre são preservados.
 */
export function simplifica(linha, tolerancia) {
  if (!(tolerancia >= 0)) throw new RangeError('tolerância deve ser >= 0');
  const n = linha.length;
  if (n <= 2) return linha.map((p) => [...p]);
  const manter = new Uint8Array(n);
  manter[0] = manter[n - 1] = 1;
  const pilha = [[0, n - 1]];
  while (pilha.length) {
    const [i, j] = pilha.pop();
    let maior = -1, idx = -1;
    for (let k = i + 1; k < j; k++) {
      const d = distanciaPontoSegmento(linha[k], linha[i], linha[j]);
      if (d > maior) { maior = d; idx = k; }
    }
    if (maior > tolerancia) {
      manter[idx] = 1;
      pilha.push([i, idx], [idx, j]);
    }
  }
  return linha.filter((_, k) => manter[k]).map((p) => [...p]);
}
