// Sutherland-Hodgman: recorta um polígono por uma janela convexa.
import { orientacao } from './segmentos.js';
import { areaComSinal } from './areaCentroide.js';

function cruzamento(a, b, c, d) {
  // Interseção das retas a-b e c-d (assume não paralelas).
  const a1 = b[1] - a[1], b1 = a[0] - b[0], c1 = a1 * a[0] + b1 * a[1];
  const a2 = d[1] - c[1], b2 = c[0] - d[0], c2 = a2 * c[0] + b2 * c[1];
  const det = a1 * b2 - a2 * b1;
  return [(b2 * c1 - b1 * c2) / det, (a1 * c2 - a2 * c1) / det];
}

/**
 * `sujeito` pode ser côncavo; `janela` deve ser convexa. Retorna o polígono
 * resultante (possivelmente vazio). Com sujeito côncavo o resultado pode
 * conter arestas degeneradas de ligação, característica do algoritmo.
 */
export function recortaPorConvexo(sujeito, janela) {
  if (janela.length < 3) throw new RangeError('janela precisa de ao menos 3 vértices');
  const jan = areaComSinal(janela) < 0 ? [...janela].reverse() : janela;
  let saida = sujeito.map((p) => [...p]);
  for (let i = 0; i < jan.length && saida.length > 0; i++) {
    const a = jan[i], b = jan[(i + 1) % jan.length];
    const entrada = saida;
    saida = [];
    for (let j = 0; j < entrada.length; j++) {
      const atual = entrada[j];
      const anterior = entrada[(j + entrada.length - 1) % entrada.length];
      const atualDentro = orientacao(a, b, atual) >= 0;
      const anteriorDentro = orientacao(a, b, anterior) >= 0;
      if (atualDentro) {
        if (!anteriorDentro) saida.push(cruzamento(anterior, atual, a, b));
        saida.push(atual);
      } else if (anteriorDentro) {
        saida.push(cruzamento(anterior, atual, a, b));
      }
    }
  }
  return saida;
}

/** Interseção de dois polígonos convexos. */
export function interseccaoConvexos(p, q) {
  return recortaPorConvexo(p, q);
}
