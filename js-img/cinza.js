import { criar } from './imagem.js';

export const PESOS = {
  bt601: [0.299, 0.587, 0.114],
  bt709: [0.2126, 0.7152, 0.0722],
};

export function luma(r, g, b, formula = 'bt601') {
  const p = PESOS[formula];
  if (!p) throw new Error(`fórmula desconhecida: ${formula}`);
  return p[0] * r + p[1] * g + p[2] * b;
}

// Plano float com a luma de cada pixel.
export function planoLuma(img, formula = 'bt601') {
  const out = new Float64Array(img.largura * img.altura);
  for (let i = 0; i < out.length; i++) {
    out[i] = luma(img.dados[i * 4], img.dados[i * 4 + 1], img.dados[i * 4 + 2], formula);
  }
  return out;
}

export function paraCinza(img, formula = 'bt601') {
  const saida = criar(img.largura, img.altura);
  const l = planoLuma(img, formula);
  for (let i = 0; i < l.length; i++) {
    const v = Math.round(l[i]);
    saida.dados[i * 4] = v;
    saida.dados[i * 4 + 1] = v;
    saida.dados[i * 4 + 2] = v;
    saida.dados[i * 4 + 3] = img.dados[i * 4 + 3];
  }
  return saida;
}

// Média simples dos canais, para comparação.
export function mediaCanais(img) {
  const saida = criar(img.largura, img.altura);
  for (let i = 0; i < img.largura * img.altura; i++) {
    const v = Math.round((img.dados[i * 4] + img.dados[i * 4 + 1] + img.dados[i * 4 + 2]) / 3);
    saida.dados.set([v, v, v, img.dados[i * 4 + 3]], i * 4);
  }
  return saida;
}
