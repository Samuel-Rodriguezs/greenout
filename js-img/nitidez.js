import { dePlanos, plano } from './imagem.js';
import { blurPlano } from './gaussiano.js';

// Unsharp mask: out = orig + quantidade * (orig - blur), ignorando diferenças abaixo de `limiar`.
export function nitidez(img, { sigma = 1, quantidade = 1, limiar = 0 } = {}) {
  const canais = [0, 1, 2].map((c) => {
    const p = plano(img, c);
    const b = blurPlano(p, img.largura, img.altura, sigma);
    const out = new Float64Array(p.length);
    for (let i = 0; i < p.length; i++) {
      const d = p[i] - b[i];
      out[i] = Math.abs(d) < limiar ? p[i] : p[i] + quantidade * d;
    }
    return out;
  });
  return dePlanos(img.largura, img.altura, canais[0], canais[1], canais[2], img);
}
