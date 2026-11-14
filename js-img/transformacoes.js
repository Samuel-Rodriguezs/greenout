import { criar, obter, definir, dentro } from './imagem.js';

export function espelharHorizontal(img) {
  const s = criar(img.largura, img.altura);
  for (let y = 0; y < img.altura; y++) {
    for (let x = 0; x < img.largura; x++) definir(s, img.largura - 1 - x, y, obter(img, x, y));
  }
  return s;
}

export function espelharVertical(img) {
  const s = criar(img.largura, img.altura);
  for (let y = 0; y < img.altura; y++) {
    for (let x = 0; x < img.largura; x++) definir(s, x, img.altura - 1 - y, obter(img, x, y));
  }
  return s;
}

export function transpor(img) {
  const s = criar(img.altura, img.largura);
  for (let y = 0; y < img.altura; y++) {
    for (let x = 0; x < img.largura; x++) definir(s, y, x, obter(img, x, y));
  }
  return s;
}

// Rotação exata em múltiplos de 90 graus, sentido horário.
export function rotacionar90(img, quartos = 1) {
  const q = ((quartos % 4) + 4) % 4;
  if (!Number.isInteger(quartos)) throw new RangeError('quartos deve ser inteiro');
  let r = img;
  for (let i = 0; i < q; i++) {
    const s = criar(r.altura, r.largura);
    for (let y = 0; y < r.altura; y++) {
      for (let x = 0; x < r.largura; x++) definir(s, r.altura - 1 - y, x, obter(r, x, y));
    }
    r = s;
  }
  return r === img ? copia(img) : r;
}

function copia(img) {
  return { largura: img.largura, altura: img.altura, dados: new Uint8ClampedArray(img.dados) };
}

// Rotação por ângulo qualquer (graus, horário) em torno do centro; mantém o tamanho.
// Mapeamento inverso com vizinho mais próximo; fora da origem usa `fundo`.
export function rotacionar(img, graus, fundo = [0, 0, 0, 0]) {
  const rad = (graus * Math.PI) / 180;
  const c = Math.cos(rad);
  const sn = Math.sin(rad);
  const cx = (img.largura - 1) / 2;
  const cy = (img.altura - 1) / 2;
  const s = criar(img.largura, img.altura, fundo);
  for (let y = 0; y < img.altura; y++) {
    for (let x = 0; x < img.largura; x++) {
      const dx = x - cx;
      const dy = y - cy;
      const sx = Math.round(c * dx + sn * dy + cx);
      const sy = Math.round(-sn * dx + c * dy + cy);
      if (dentro(img, sx, sy)) definir(s, x, y, obter(img, sx, sy));
    }
  }
  return s;
}
