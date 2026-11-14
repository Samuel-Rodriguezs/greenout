import { clonar } from './imagem.js';

// Aplica uma tabela de 256 entradas aos canais RGB (alfa preservado).
export function aplicarLUT(img, lut) {
  const s = clonar(img);
  for (let i = 0; i < img.dados.length; i += 4) {
    s.dados[i] = lut[img.dados[i]];
    s.dados[i + 1] = lut[img.dados[i + 1]];
    s.dados[i + 2] = lut[img.dados[i + 2]];
  }
  return s;
}

function lutDe(f) {
  const lut = new Float64Array(256);
  for (let v = 0; v < 256; v++) lut[v] = Math.round(Math.min(255, Math.max(0, f(v))));
  return lut;
}

export const brilho = (img, delta) => aplicarLUT(img, lutDe((v) => v + delta));

// fator > 1 aumenta o contraste em torno do cinza médio 128.
export const contraste = (img, fator) => aplicarLUT(img, lutDe((v) => (v - 128) * fator + 128));

// out = 255 * (v/255)^(1/g)
export function gama(img, g) {
  if (!(g > 0)) throw new RangeError('gama deve ser positivo');
  return aplicarLUT(img, lutDe((v) => 255 * Math.pow(v / 255, 1 / g)));
}

// Curva por pontos de controle [[entrada, saída], ...] com interpolação linear.
export function curva(img, pontos) {
  const p = [...pontos].sort((a, b) => a[0] - b[0]);
  if (p.length < 2) throw new Error('são necessários ao menos 2 pontos');
  const f = (v) => {
    if (v <= p[0][0]) return p[0][1];
    if (v >= p[p.length - 1][0]) return p[p.length - 1][1];
    let k = 1;
    while (p[k][0] < v) k++;
    const [x0, y0] = p[k - 1];
    const [x1, y1] = p[k];
    return y0 + ((y1 - y0) * (v - x0)) / (x1 - x0);
  };
  return aplicarLUT(img, lutDe(f));
}
