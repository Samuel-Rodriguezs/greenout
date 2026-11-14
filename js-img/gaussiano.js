import { convolverPlano } from './convolucao.js';
import { porCanal } from './imagem.js';

// Kernel 1D gaussiano normalizado (soma 1). Raio padrão = ceil(3*sigma).
export function kernelGaussiano(sigma, raio = Math.ceil(3 * sigma)) {
  if (!(sigma > 0)) throw new RangeError('sigma deve ser positivo');
  const k = [];
  let soma = 0;
  for (let i = -raio; i <= raio; i++) {
    const v = Math.exp(-(i * i) / (2 * sigma * sigma));
    k.push(v);
    soma += v;
  }
  return k.map((v) => v / soma);
}

// Blur separável em planos float: horizontal depois vertical.
export function blurPlano(p, largura, altura, sigma, borda = 'clamp') {
  const k = kernelGaussiano(sigma);
  const h = convolverPlano(p, largura, altura, [k], borda);
  return convolverPlano(h, largura, altura, k.map((v) => [v]), borda);
}

export function blurGaussiano(img, sigma, borda = 'clamp') {
  return porCanal(img, (p) => blurPlano(p, img.largura, img.altura, sigma, borda));
}
