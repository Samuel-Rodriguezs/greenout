import { indiceBorda, plano, dePlanos } from './imagem.js';

function medianaPlano(p, l, a, raio, borda) {
  const out = new Float64Array(l * a);
  const janela = [];
  for (let y = 0; y < a; y++) {
    for (let x = 0; x < l; x++) {
      janela.length = 0;
      for (let dy = -raio; dy <= raio; dy++) {
        const yy = indiceBorda(y + dy, a, borda);
        if (yy < 0) continue;
        for (let dx = -raio; dx <= raio; dx++) {
          const xx = indiceBorda(x + dx, l, borda);
          if (xx >= 0) janela.push(p[yy * l + xx]);
        }
      }
      janela.sort((u, v) => u - v);
      const m = janela.length >> 1;
      out[y * l + x] = janela.length % 2 ? janela[m] : (janela[m - 1] + janela[m]) / 2;
    }
  }
  return out;
}

// Filtro de mediana (janela (2*raio+1)^2) em cada canal RGB.
export function mediana(img, raio = 1, borda = 'clamp') {
  if (!Number.isInteger(raio) || raio < 1) throw new RangeError('raio deve ser inteiro >= 1');
  const [r, g, b] = [0, 1, 2].map((c) => medianaPlano(plano(img, c), img.largura, img.altura, raio, borda));
  return dePlanos(img.largura, img.altura, r, g, b, img);
}
