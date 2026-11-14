import { planoLuma } from './cinza.js';
import { aplicarLUT } from './tons.js';

// Histograma de 256 posições da luma (BT.601 arredondada) ou de um canal 0..3.
export function histograma(img, canal = 'luma') {
  const h = new Array(256).fill(0);
  if (canal === 'luma') {
    for (const v of planoLuma(img)) h[Math.round(v)]++;
  } else {
    for (let i = 0; i < img.largura * img.altura; i++) h[img.dados[i * 4 + canal]]++;
  }
  return h;
}

export function acumulado(h) {
  const c = new Array(h.length);
  let s = 0;
  for (let i = 0; i < h.length; i++) c[i] = s += h[i];
  return c;
}

// Estatísticas: média, mediana e desvio da distribuição.
export function estatisticas(h) {
  const n = h.reduce((a, b) => a + b, 0);
  const media = h.reduce((a, c, v) => a + c * v, 0) / n;
  const variancia = h.reduce((a, c, v) => a + c * (v - media) ** 2, 0) / n;
  const c = acumulado(h);
  const mediana = c.findIndex((x) => x >= n / 2);
  return { media, mediana, desvio: Math.sqrt(variancia) };
}

// Equalização: LUT = round((cdf - cdfmin)/(N - cdfmin) * 255), calculada na luma
// e aplicada a R, G e B (exata para imagens em tons de cinza).
export function equalizar(img) {
  const h = histograma(img);
  const c = acumulado(h);
  const n = img.largura * img.altura;
  const cdfMin = c.find((x) => x > 0);
  const lut = new Uint8Array(256);
  if (n === cdfMin) {
    for (let v = 0; v < 256; v++) lut[v] = v;
  } else {
    for (let v = 0; v < 256; v++) lut[v] = Math.round(((Math.max(c[v], cdfMin) - cdfMin) / (n - cdfMin)) * 255);
  }
  return aplicarLUT(img, lut);
}

// Esticamento linear de contraste entre os extremos reais.
export function esticar(img) {
  const h = histograma(img);
  const min = h.findIndex((x) => x > 0);
  const max = 255 - [...h].reverse().findIndex((x) => x > 0);
  const lut = new Uint8Array(256);
  for (let v = 0; v < 256; v++) lut[v] = max === min ? v : Math.round(((v - min) / (max - min)) * 255);
  return aplicarLUT(img, lut);
}
