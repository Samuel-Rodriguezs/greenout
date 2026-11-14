// Distância de um ponto a um polígono (e ao seu contorno).
import { distanciaPontoSegmento } from './rdp.js';
import { classificaPonto } from './pontoEmPoligono.js';

/** Menor distância do ponto ao contorno (arestas) do polígono. */
export function distanciaAoContorno(p, poligono) {
  if (poligono.length < 3) throw new RangeError('polígono precisa de ao menos 3 vértices');
  let melhor = Infinity;
  for (let i = 0; i < poligono.length; i++) {
    const d = distanciaPontoSegmento(p, poligono[i], poligono[(i + 1) % poligono.length]);
    if (d < melhor) melhor = d;
  }
  return melhor;
}

/** Distância ao polígono preenchido: 0 se dentro ou na borda. */
export function distanciaPontoPoligono(p, poligono) {
  return classificaPonto(p, poligono) === 'fora' ? distanciaAoContorno(p, poligono) : 0;
}

/** Distância com sinal: negativa dentro, positiva fora, 0 na borda. */
export function distanciaComSinal(p, poligono) {
  const c = classificaPonto(p, poligono);
  if (c === 'borda') return 0;
  const d = distanciaAoContorno(p, poligono);
  return c === 'dentro' ? -d : d;
}

/** Ponto do contorno mais próximo de p. */
export function pontoMaisProximoNoContorno(p, poligono) {
  let melhor = null, melhorD = Infinity;
  for (let i = 0; i < poligono.length; i++) {
    const a = poligono[i], b = poligono[(i + 1) % poligono.length];
    const dx = b[0] - a[0], dy = b[1] - a[1];
    const l2 = dx * dx + dy * dy;
    const t = l2 === 0 ? 0 : Math.max(0, Math.min(1, ((p[0] - a[0]) * dx + (p[1] - a[1]) * dy) / l2));
    const q = [a[0] + t * dx, a[1] + t * dy];
    const d = Math.hypot(p[0] - q[0], p[1] - q[1]);
    if (d < melhorD) { melhorD = d; melhor = q; }
  }
  return melhor;
}
