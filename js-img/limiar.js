import { clonar, criar } from './imagem.js';
import { planoLuma } from './cinza.js';

export function inverter(img) {
  const s = clonar(img);
  for (let i = 0; i < s.dados.length; i += 4) {
    s.dados[i] = 255 - s.dados[i];
    s.dados[i + 1] = 255 - s.dados[i + 1];
    s.dados[i + 2] = 255 - s.dados[i + 2];
  }
  return s;
}

// Luma > t vira branco (255), senão preto (0).
export function limiarizar(img, t) {
  const l = planoLuma(img);
  const s = criar(img.largura, img.altura);
  for (let i = 0; i < l.length; i++) {
    const v = l[i] > t ? 255 : 0;
    s.dados.set([v, v, v, img.dados[i * 4 + 3]], i * 4);
  }
  return s;
}

// Limiar de Otsu (classe escura: luma <= t). Devolve o menor t de variância máxima.
export function otsu(img) {
  const h = new Array(256).fill(0);
  for (const v of planoLuma(img)) h[Math.round(v)]++;
  const total = img.largura * img.altura;
  let somaTotal = 0;
  for (let i = 0; i < 256; i++) somaTotal += i * h[i];
  let wB = 0;
  let somaB = 0;
  let melhor = -1;
  let t = 0;
  for (let i = 0; i < 256; i++) {
    wB += h[i];
    if (wB === 0) continue;
    const wF = total - wB;
    if (wF === 0) break;
    somaB += i * h[i];
    const mB = somaB / wB;
    const mF = (somaTotal - somaB) / wF;
    const varEntre = wB * wF * (mB - mF) ** 2;
    if (varEntre > melhor) {
      melhor = varEntre;
      t = i;
    }
  }
  return t;
}

export const limiarOtsu = (img) => limiarizar(img, otsu(img));
