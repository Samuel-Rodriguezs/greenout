import { planoLuma } from './cinza.js';

function mesmoTamanho(a, b) {
  if (a.largura !== b.largura || a.altura !== b.altura) throw new RangeError('imagens de tamanhos diferentes');
}

// Erro quadrático médio sobre os canais R, G e B.
export function mse(a, b) {
  mesmoTamanho(a, b);
  let soma = 0;
  const n = a.largura * a.altura;
  for (let i = 0; i < n; i++) {
    for (let c = 0; c < 3; c++) soma += (a.dados[i * 4 + c] - b.dados[i * 4 + c]) ** 2;
  }
  return soma / (n * 3);
}

export function psnr(a, b) {
  const e = mse(a, b);
  return e === 0 ? Infinity : 10 * Math.log10((255 * 255) / e);
}

const C1 = (0.01 * 255) ** 2;
const C2 = (0.03 * 255) ** 2;

function ssimJanela(x, y) {
  const n = x.length;
  const mx = x.reduce((s, v) => s + v, 0) / n;
  const my = y.reduce((s, v) => s + v, 0) / n;
  let vx = 0;
  let vy = 0;
  let cov = 0;
  for (let i = 0; i < n; i++) {
    vx += (x[i] - mx) ** 2;
    vy += (y[i] - my) ** 2;
    cov += (x[i] - mx) * (y[i] - my);
  }
  vx /= n;
  vy /= n;
  cov /= n;
  return ((2 * mx * my + C1) * (2 * cov + C2)) / ((mx * mx + my * my + C1) * (vx + vy + C2));
}

// SSIM simples sobre a luma: média das janelas tam x tam (sem sobreposição).
// Com tam = 0 usa a imagem inteira como uma única janela (SSIM global).
export function ssim(a, b, tam = 0) {
  mesmoTamanho(a, b);
  const la = planoLuma(a);
  const lb = planoLuma(b);
  if (tam === 0) return ssimJanela(Array.from(la), Array.from(lb));
  let soma = 0;
  let cont = 0;
  for (let y0 = 0; y0 < a.altura; y0 += tam) {
    for (let x0 = 0; x0 < a.largura; x0 += tam) {
      const xs = [];
      const ys = [];
      for (let y = y0; y < Math.min(a.altura, y0 + tam); y++) {
        for (let x = x0; x < Math.min(a.largura, x0 + tam); x++) {
          xs.push(la[y * a.largura + x]);
          ys.push(lb[y * a.largura + x]);
        }
      }
      soma += ssimJanela(xs, ys);
      cont++;
    }
  }
  return soma / cont;
}
