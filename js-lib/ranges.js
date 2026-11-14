// Gera sequência numérica [inicio, fim) com passo (pode ser negativo).
export function range(inicio, fim, passo = 1) {
  if (fim === undefined) { fim = inicio; inicio = 0; }
  if (passo === 0) throw new RangeError('passo não pode ser 0');
  const r = [];
  if (passo > 0) for (let i = inicio; i < fim; i += passo) r.push(i);
  else for (let i = inicio; i > fim; i += passo) r.push(i);
  return r;
}
// Verifica se um valor está em [min, max].
export const emIntervalo = (v, min, max) => v >= min && v <= max;
// Une intervalos [a,b] sobrepostos ou adjacentes (inteiros).
export function mesclarIntervalos(intervalos) {
  const ord = intervalos.map(([a, b]) => [a, b]).sort((x, y) => x[0] - y[0]);
  const saida = [];
  for (const [a, b] of ord) {
    const ult = saida[saida.length - 1];
    if (ult && a <= ult[1] + 1) ult[1] = Math.max(ult[1], b);
    else saida.push([a, b]);
  }
  return saida;
}
