// Bounding box / AABB 2D imutável: { minX, minY, maxX, maxY }.

export function criaBBox(minX, minY, maxX, maxY) {
  if (minX > maxX || minY > maxY) throw new RangeError('caixa invertida');
  return Object.freeze({ minX, minY, maxX, maxY });
}

export function bboxDePontos(pontos) {
  if (pontos.length === 0) throw new RangeError('sem pontos');
  let minX = Infinity, minY = Infinity, maxX = -Infinity, maxY = -Infinity;
  for (const [x, y] of pontos) {
    if (x < minX) minX = x;
    if (x > maxX) maxX = x;
    if (y < minY) minY = y;
    if (y > maxY) maxY = y;
  }
  return criaBBox(minX, minY, maxX, maxY);
}

export const largura = (b) => b.maxX - b.minX;
export const altura = (b) => b.maxY - b.minY;
export const areaBBox = (b) => largura(b) * altura(b);
export const centroBBox = (b) => [(b.minX + b.maxX) / 2, (b.minY + b.maxY) / 2];

export function contemPonto(b, [x, y]) {
  return x >= b.minX && x <= b.maxX && y >= b.minY && y <= b.maxY;
}

export function contemBBox(a, b) {
  return b.minX >= a.minX && b.maxX <= a.maxX && b.minY >= a.minY && b.maxY <= a.maxY;
}

/** Tocar na borda conta como interseção. */
export function intersecta(a, b) {
  return a.minX <= b.maxX && a.maxX >= b.minX && a.minY <= b.maxY && a.maxY >= b.minY;
}

/** Interseção das caixas, ou null se disjuntas. */
export function interseccao(a, b) {
  if (!intersecta(a, b)) return null;
  return criaBBox(Math.max(a.minX, b.minX), Math.max(a.minY, b.minY), Math.min(a.maxX, b.maxX), Math.min(a.maxY, b.maxY));
}

export function uniao(a, b) {
  return criaBBox(Math.min(a.minX, b.minX), Math.min(a.minY, b.minY), Math.max(a.maxX, b.maxX), Math.max(a.maxY, b.maxY));
}

export function expande(b, margem) {
  return criaBBox(b.minX - margem, b.minY - margem, b.maxX + margem, b.maxY + margem);
}

/** Distância mínima de um ponto à caixa (0 se dentro). */
export function distanciaAoPonto(b, [x, y]) {
  const dx = Math.max(b.minX - x, 0, x - b.maxX);
  const dy = Math.max(b.minY - y, 0, y - b.maxY);
  return Math.hypot(dx, dy);
}
