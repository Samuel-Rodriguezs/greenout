import { indiceBorda, porCanal } from './imagem.js';

// Convolução 2D verdadeira (kernel espelhado) sobre um plano float.
// kernel: array de linhas; origem no centro (floor(n/2)). Retorna Float64Array.
export function convolverPlano(p, largura, altura, kernel, borda = 'clamp') {
  const kh = kernel.length;
  const kw = kernel[0].length;
  const cx = Math.floor(kw / 2);
  const cy = Math.floor(kh / 2);
  const out = new Float64Array(largura * altura);
  for (let y = 0; y < altura; y++) {
    for (let x = 0; x < largura; x++) {
      let s = 0;
      for (let j = 0; j < kh; j++) {
        const yy = indiceBorda(y - (j - cy), altura, borda);
        if (yy < 0) continue;
        for (let i = 0; i < kw; i++) {
          const xx = indiceBorda(x - (i - cx), largura, borda);
          if (xx < 0) continue;
          s += kernel[j][i] * p[yy * largura + xx];
        }
      }
      out[y * largura + x] = s;
    }
  }
  return out;
}

// Convolução de uma imagem RGBA (canais RGB; alfa preservado).
export function convolver(img, kernel, { borda = 'clamp', divisor = 1, offset = 0 } = {}) {
  if (divisor === 0) throw new RangeError('divisor zero');
  return porCanal(img, (p) => {
    const r = convolverPlano(p, img.largura, img.altura, kernel, borda);
    for (let i = 0; i < r.length; i++) r[i] = r[i] / divisor + offset;
    return r;
  });
}

export const KERNELS = {
  identidade: [[0, 0, 0], [0, 1, 0], [0, 0, 0]],
  caixa3: [[1, 1, 1], [1, 1, 1], [1, 1, 1]].map((l) => l.map((v) => v / 9)),
  relevo: [[-2, -1, 0], [-1, 1, 1], [0, 1, 2]],
  realce: [[0, -1, 0], [-1, 5, -1], [0, -1, 0]],
};
