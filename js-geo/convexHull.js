// Fecho convexo pelo algoritmo de Andrew (monotone chain), O(n log n).
import { orientacao } from './segmentos.js';

/**
 * Devolve os vértices do fecho em ordem anti-horária, começando pelo ponto
 * mais à esquerda/embaixo. Pontos colineares na borda são descartados.
 */
export function convexHull(pontos) {
  const unicos = [...new Map(pontos.map((p) => [`${p[0]},${p[1]}`, p])).values()];
  unicos.sort((a, b) => a[0] - b[0] || a[1] - b[1]);
  if (unicos.length <= 2) return unicos.map((p) => [...p]);

  const meia = (seq) => {
    const h = [];
    for (const p of seq) {
      while (h.length >= 2 && orientacao(h[h.length - 2], h[h.length - 1], p) <= 0) h.pop();
      h.push(p);
    }
    h.pop();
    return h;
  };
  const inferior = meia(unicos);
  const superior = meia([...unicos].reverse());
  const hull = inferior.concat(superior);
  return hull.map((p) => [...p]);
}
