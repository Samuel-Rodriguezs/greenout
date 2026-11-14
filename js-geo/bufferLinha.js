// Buffer simples de polilinha: contorno com tampas arredondadas e quinas em
// mitra (limitada a 2x a distância). Devolve um anel anti-horário.
import { areaComSinal } from './areaCentroide.js';

function normalEsquerda(a, b) {
  const dx = b[0] - a[0], dy = b[1] - a[1];
  const l = Math.hypot(dx, dy);
  return [-dy / l, dx / l];
}

function lado(pts, d) {
  // Deslocamento de cada vértice para a esquerda do sentido de percurso.
  const saida = [];
  for (let i = 0; i < pts.length; i++) {
    const nA = i > 0 ? normalEsquerda(pts[i - 1], pts[i]) : null;
    const nB = i < pts.length - 1 ? normalEsquerda(pts[i], pts[i + 1]) : null;
    if (!nA || !nB) {
      const n = nA ?? nB;
      saida.push([pts[i][0] + n[0] * d, pts[i][1] + n[1] * d]);
      continue;
    }
    let mx = nA[0] + nB[0], my = nA[1] + nB[1];
    const ml = Math.hypot(mx, my);
    if (ml < 1e-9) { // retorno de 180 graus: usa a normal de entrada
      saida.push([pts[i][0] + nA[0] * d, pts[i][1] + nA[1] * d]);
      continue;
    }
    mx /= ml; my /= ml;
    const cos = mx * nA[0] + my * nA[1]; // cos(meio-ângulo)
    const comp = Math.min(d / cos, 2 * d);
    saida.push([pts[i][0] + mx * comp, pts[i][1] + my * comp]);
  }
  return saida;
}

function tampa(centro, de, d, passos) {
  // Semicírculo a partir do ponto `de` (em torno de `centro`), girando 180 graus no sentido horário (de um lado ao outro da linha).
  const a0 = Math.atan2(de[1] - centro[1], de[0] - centro[0]);
  const arco = [];
  for (let k = 1; k < passos; k++) {
    const a = a0 - (Math.PI * k) / passos;
    arco.push([centro[0] + Math.cos(a) * d, centro[1] + Math.sin(a) * d]);
  }
  return arco;
}

export function bufferLinha(linha, distancia, { passosTampa = 8 } = {}) {
  if (!(distancia > 0)) throw new RangeError('distância deve ser > 0');
  const pts = linha.filter((p, i) => i === 0 || p[0] !== linha[i - 1][0] || p[1] !== linha[i - 1][1]);
  if (pts.length === 0) throw new RangeError('linha vazia');
  if (pts.length === 1) {
    const [x, y] = pts[0];
    const n = passosTampa * 2;
    return Array.from({ length: n }, (_, k) => [
      x + Math.cos((2 * Math.PI * k) / n) * distancia,
      y + Math.sin((2 * Math.PI * k) / n) * distancia,
    ]);
  }
  const esq = lado(pts, distancia);
  const rev = [...pts].reverse();
  const dir = lado(rev, distancia); // lado direito do percurso original, já invertido
  const fim = tampa(pts.at(-1), esq.at(-1), distancia, passosTampa);
  const inicio = tampa(pts[0], dir.at(-1), distancia, passosTampa);
  const anel = [...esq, ...fim, ...dir, ...inicio];
  return areaComSinal(anel) < 0 ? anel.reverse() : anel;
}
