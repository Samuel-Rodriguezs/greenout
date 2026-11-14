import { deCinza } from './imagem.js';
import { planoLuma } from './cinza.js';

// Floyd-Steinberg: limiar 128 com difusão de erro (7,3,5,1)/16. Saída binária 0/255.
export function floydSteinberg(img) {
  const l = img.largura;
  const a = img.altura;
  const p = planoLuma(img).map(Math.round); // luma de 8 bits (evita ruído de ponto flutuante)
  const out = new Array(l * a);
  const difundir = (x, y, e) => {
    if (x >= 0 && x < l && y < a) p[y * l + x] += e;
  };
  for (let y = 0; y < a; y++) {
    for (let x = 0; x < l; x++) {
      const velho = p[y * l + x];
      const novo = velho >= 128 ? 255 : 0;
      out[y * l + x] = novo;
      const e = velho - novo;
      difundir(x + 1, y, (e * 7) / 16);
      difundir(x - 1, y + 1, (e * 3) / 16);
      difundir(x, y + 1, (e * 5) / 16);
      difundir(x + 1, y + 1, e / 16);
    }
  }
  return deCinza(l, a, out);
}

// Matriz de Bayer n x n (n potência de 2) com valores 0..n*n-1.
export function matrizBayer(n) {
  if (n < 2 || (n & (n - 1)) !== 0) throw new RangeError('n deve ser potência de 2 >= 2');
  let m = [[0, 2], [3, 1]];
  for (let t = 2; t < n; t *= 2) {
    const g = new Array(t * 2).fill(0).map(() => new Array(t * 2).fill(0));
    for (let y = 0; y < t; y++) {
      for (let x = 0; x < t; x++) {
        const v = 4 * m[y][x];
        g[y][x] = v;
        g[y][x + t] = v + 2;
        g[y + t][x] = v + 3;
        g[y + t][x + t] = v + 1;
      }
    }
    m = g;
  }
  return m;
}

// Dithering ordenado: limiar do pixel = (M + 0.5)/n² * 255.
export function ordenadoBayer(img, n = 4) {
  const m = matrizBayer(n);
  const p = planoLuma(img).map(Math.round); // luma de 8 bits (evita ruído de ponto flutuante)
  const out = new Array(p.length);
  for (let y = 0; y < img.altura; y++) {
    for (let x = 0; x < img.largura; x++) {
      const limiar = ((m[y % n][x % n] + 0.5) / (n * n)) * 255;
      out[y * img.largura + x] = p[y * img.largura + x] > limiar ? 255 : 0;
    }
  }
  return deCinza(img.largura, img.altura, out);
}
