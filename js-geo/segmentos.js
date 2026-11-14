// Orientação de três pontos e interseção de segmentos. Pontos são [x, y].

/** > 0 anti-horário, < 0 horário, 0 colinear. */
export function orientacao(a, b, c) {
  return (b[0] - a[0]) * (c[1] - a[1]) - (b[1] - a[1]) * (c[0] - a[0]);
}

const sinal = (v) => (v > 0 ? 1 : v < 0 ? -1 : 0);

/** Assume c colinear com a-b: c está dentro da caixa do segmento? */
function dentroDaCaixa(a, b, c) {
  return (
    Math.min(a[0], b[0]) <= c[0] && c[0] <= Math.max(a[0], b[0]) &&
    Math.min(a[1], b[1]) <= c[1] && c[1] <= Math.max(a[1], b[1])
  );
}

/** Verdadeiro se os segmentos p1-p2 e p3-p4 compartilham ao menos um ponto. */
export function segmentosSeInterceptam(p1, p2, p3, p4) {
  const o1 = sinal(orientacao(p1, p2, p3));
  const o2 = sinal(orientacao(p1, p2, p4));
  const o3 = sinal(orientacao(p3, p4, p1));
  const o4 = sinal(orientacao(p3, p4, p2));
  if (o1 !== o2 && o3 !== o4) return true;
  if (o1 === 0 && dentroDaCaixa(p1, p2, p3)) return true;
  if (o2 === 0 && dentroDaCaixa(p1, p2, p4)) return true;
  if (o3 === 0 && dentroDaCaixa(p3, p4, p1)) return true;
  if (o4 === 0 && dentroDaCaixa(p3, p4, p2)) return true;
  return false;
}

/**
 * Ponto único de interseção, ou null se não se cruzam ou são paralelos
 * (inclusive colineares sobrepostos, onde não há ponto único).
 */
export function pontoDeInterseccao(p1, p2, p3, p4) {
  const rx = p2[0] - p1[0], ry = p2[1] - p1[1];
  const sx = p4[0] - p3[0], sy = p4[1] - p3[1];
  const den = rx * sy - ry * sx;
  if (den === 0) return null;
  const qpx = p3[0] - p1[0], qpy = p3[1] - p1[1];
  const t = (qpx * sy - qpy * sx) / den;
  const u = (qpx * ry - qpy * rx) / den;
  if (t < 0 || t > 1 || u < 0 || u > 1) return null;
  return [p1[0] + t * rx, p1[1] + t * ry];
}
