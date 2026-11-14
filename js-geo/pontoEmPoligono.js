// Ponto em polígono: winding number com classificação de borda.
import { orientacao } from './segmentos.js';

function naBorda(p, a, b) {
  if (orientacao(a, b, p) !== 0) return false;
  return (
    Math.min(a[0], b[0]) <= p[0] && p[0] <= Math.max(a[0], b[0]) &&
    Math.min(a[1], b[1]) <= p[1] && p[1] <= Math.max(a[1], b[1])
  );
}

/**
 * Classifica `p` em relação a um polígono simples (anel aberto, sem repetir
 * o primeiro vértice no fim; se repetir, é ignorado).
 * Retorna 'dentro' | 'borda' | 'fora'.
 */
export function classificaPonto(p, poligono) {
  let anel = poligono;
  const n0 = anel.length;
  if (n0 > 1 && anel[0][0] === anel[n0 - 1][0] && anel[0][1] === anel[n0 - 1][1]) {
    anel = anel.slice(0, -1);
  }
  const n = anel.length;
  if (n < 3) throw new RangeError('polígono precisa de ao menos 3 vértices');
  let wn = 0;
  for (let i = 0; i < n; i++) {
    const a = anel[i], b = anel[(i + 1) % n];
    if (naBorda(p, a, b)) return 'borda';
    if (a[1] <= p[1]) {
      if (b[1] > p[1] && orientacao(a, b, p) > 0) wn++;
    } else if (b[1] <= p[1] && orientacao(a, b, p) < 0) {
      wn--;
    }
  }
  return wn !== 0 ? 'dentro' : 'fora';
}

/** Verdadeiro se o ponto está dentro ou na borda (comportamento configurável). */
export function pontoEmPoligono(p, poligono, { incluiBorda = true } = {}) {
  const c = classificaPonto(p, poligono);
  return c === 'dentro' || (incluiBorda && c === 'borda');
}
