import { convolverPlano } from './convolucao.js';
import { deCinza, porCanal } from './imagem.js';
import { planoLuma } from './cinza.js';

export const LAPLACIANO_4 = [[0, 1, 0], [1, -4, 1], [0, 1, 0]];
export const LAPLACIANO_8 = [[1, 1, 1], [1, -8, 1], [1, 1, 1]];

const kernelDe = (conectividade) => {
  if (conectividade === 4) return LAPLACIANO_4;
  if (conectividade === 8) return LAPLACIANO_8;
  throw new Error('conectividade deve ser 4 ou 8');
};

// Resposta com sinal (float) sobre um plano.
export function laplacianoPlano(p, l, a, conectividade = 4, borda = 'clamp') {
  return convolverPlano(p, l, a, kernelDe(conectividade), borda);
}

// |Laplaciano| da luma, saturado em 255.
export function laplaciano(img, conectividade = 4) {
  const r = laplacianoPlano(planoLuma(img), img.largura, img.altura, conectividade);
  return deCinza(img.largura, img.altura, Array.from(r, (v) => Math.min(255, Math.round(Math.abs(v)))));
}

// Realce: out = orig - laplaciano (centro negativo).
export function realcarLaplaciano(img, conectividade = 4) {
  return porCanal(img, (p) => {
    const lap = laplacianoPlano(p, img.largura, img.altura, conectividade);
    return p.map((v, i) => v - lap[i]);
  });
}
