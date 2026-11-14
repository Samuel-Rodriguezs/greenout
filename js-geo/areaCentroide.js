// Área (fórmula do cadarço) e centroide de polígonos simples.

/** Área com sinal: positiva se anti-horário, negativa se horário. */
export function areaComSinal(poligono) {
  const n = poligono.length;
  let soma = 0;
  for (let i = 0; i < n; i++) {
    const [x1, y1] = poligono[i];
    const [x2, y2] = poligono[(i + 1) % n];
    soma += x1 * y2 - x2 * y1;
  }
  return soma / 2;
}

export function area(poligono) {
  return Math.abs(areaComSinal(poligono));
}

export function ehAntiHorario(poligono) {
  return areaComSinal(poligono) > 0;
}

export function perimetro(poligono) {
  let p = 0;
  for (let i = 0; i < poligono.length; i++) {
    const a = poligono[i], b = poligono[(i + 1) % poligono.length];
    p += Math.hypot(b[0] - a[0], b[1] - a[1]);
  }
  return p;
}

/** Centroide da região. Para área nula (degenerado) lança RangeError. */
export function centroide(poligono) {
  const n = poligono.length;
  const a = areaComSinal(poligono);
  if (a === 0) throw new RangeError('polígono degenerado: área zero');
  let cx = 0, cy = 0;
  for (let i = 0; i < n; i++) {
    const [x1, y1] = poligono[i];
    const [x2, y2] = poligono[(i + 1) % n];
    const f = x1 * y2 - x2 * y1;
    cx += (x1 + x2) * f;
    cy += (y1 + y2) * f;
  }
  return [cx / (6 * a), cy / (6 * a)];
}

/** Média dos vértices (útil para nuvens de pontos). */
export function mediaDosPontos(pontos) {
  if (pontos.length === 0) throw new RangeError('lista vazia');
  let sx = 0, sy = 0;
  for (const [x, y] of pontos) { sx += x; sy += y; }
  return [sx / pontos.length, sy / pontos.length];
}
