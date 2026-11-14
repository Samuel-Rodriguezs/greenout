// Triangulação de polígono simples por ear clipping, O(n²).
import { orientacao } from './segmentos.js';
import { areaComSinal } from './areaCentroide.js';

function pontoNoTriangulo(p, a, b, c) {
  // a, b, c em ordem anti-horária; bordas contam como dentro.
  return orientacao(a, b, p) >= 0 && orientacao(b, c, p) >= 0 && orientacao(c, a, p) >= 0;
}

/**
 * Retorna triângulos como trios de índices do polígono original, todos em
 * ordem anti-horária. Lança Error se o polígono não for simples.
 */
export function triangula(poligono) {
  const n = poligono.length;
  if (n < 3) throw new RangeError('polígono precisa de ao menos 3 vértices');
  const horario = areaComSinal(poligono) < 0;
  const restantes = Array.from({ length: n }, (_, i) => i);
  if (horario) restantes.reverse();
  const P = (i) => poligono[i];
  const triangulos = [];

  let tentativas = 0;
  let i = 0;
  while (restantes.length > 3) {
    const m = restantes.length;
    const ia = restantes[(i + m - 1) % m], ib = restantes[i % m], ic = restantes[(i + 1) % m];
    const a = P(ia), b = P(ib), c = P(ic);
    let orelha = orientacao(a, b, c) > 0; // vértice convexo
    if (orelha) {
      for (const k of restantes) {
        if (k === ia || k === ib || k === ic) continue;
        const q = P(k);
        // Ignora vértices coincidentes com os do triângulo (polígonos com vértice repetido).
        if ((q[0] === a[0] && q[1] === a[1]) || (q[0] === b[0] && q[1] === b[1]) || (q[0] === c[0] && q[1] === c[1])) continue;
        if (pontoNoTriangulo(q, a, b, c)) { orelha = false; break; }
      }
    }
    if (orelha) {
      triangulos.push([ia, ib, ic]);
      restantes.splice(i % m, 1);
      tentativas = 0;
      i = i % restantes.length;
    } else {
      i = (i + 1) % m;
      if (++tentativas > m) {
        // Vértices colineares podem não formar orelha: descarta um e segue.
        const col = restantes.findIndex((_, k) => {
          const mm = restantes.length;
          return orientacao(P(restantes[(k + mm - 1) % mm]), P(restantes[k]), P(restantes[(k + 1) % mm])) === 0;
        });
        if (col === -1) throw new Error('polígono não é simples: não há orelha disponível');
        restantes.splice(col, 1);
        tentativas = 0;
        i = i % restantes.length;
      }
    }
  }
  const [x, y, z] = restantes;
  if (orientacao(P(x), P(y), P(z)) !== 0) triangulos.push([x, y, z]);
  return triangulos;
}
