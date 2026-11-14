import { deCinza } from './imagem.js';
import { planoLuma } from './cinza.js';
import { blurPlano } from './gaussiano.js';

const amostra = (p, l, a, x, y) => p[Math.min(a - 1, Math.max(0, y)) * l + Math.min(l - 1, Math.max(0, x))];

// Gradientes de Sobel (borda clamp). Retorna {gx, gy, mag}.
export function sobelPlanos(p, l, a) {
  const gx = new Float64Array(l * a);
  const gy = new Float64Array(l * a);
  const mag = new Float64Array(l * a);
  for (let y = 0; y < a; y++) {
    for (let x = 0; x < l; x++) {
      const s = (dx, dy) => amostra(p, l, a, x + dx, y + dy);
      const sx = s(1, -1) + 2 * s(1, 0) + s(1, 1) - (s(-1, -1) + 2 * s(-1, 0) + s(-1, 1));
      const sy = s(-1, 1) + 2 * s(0, 1) + s(1, 1) - (s(-1, -1) + 2 * s(0, -1) + s(1, -1));
      const i = y * l + x;
      gx[i] = sx;
      gy[i] = sy;
      mag[i] = Math.hypot(sx, sy);
    }
  }
  return { gx, gy, mag };
}

// Imagem cinza com a magnitude de Sobel saturada em 255.
export function sobel(img) {
  const { mag } = sobelPlanos(planoLuma(img), img.largura, img.altura);
  return deCinza(img.largura, img.altura, Array.from(mag, (v) => Math.min(255, Math.round(v))));
}

// Canny simplificado: blur gaussiano, Sobel, supressão de não-máximos e histerese.
// Retorna imagem binária (255 = borda).
export function canny(img, { sigma = 1, baixo = 30, alto = 90 } = {}) {
  const l = img.largura;
  const a = img.altura;
  const p = blurPlano(planoLuma(img), l, a, sigma);
  const { gx, gy, mag } = sobelPlanos(p, l, a);
  const m = (x, y) => (x < 0 || y < 0 || x >= l || y >= a ? 0 : mag[y * l + x]);

  // Supressão: compara com os dois vizinhos na direção do gradiente (quantizada em 4).
  const nms = new Float64Array(l * a);
  for (let y = 0; y < a; y++) {
    for (let x = 0; x < l; x++) {
      const i = y * l + x;
      if (mag[i] === 0) continue;
      let ang = (Math.atan2(gy[i], gx[i]) * 180) / Math.PI;
      if (ang < 0) ang += 180;
      let dx;
      let dy;
      if (ang < 22.5 || ang >= 157.5) [dx, dy] = [1, 0];
      else if (ang < 67.5) [dx, dy] = [1, 1];
      else if (ang < 112.5) [dx, dy] = [0, 1];
      else [dx, dy] = [1, -1];
      if (mag[i] >= m(x - dx, y - dy) && mag[i] > m(x + dx, y + dy)) nms[i] = mag[i];
    }
  }

  // Histerese: fortes sementes; fracos entram se ligados (8-vizinhança) a uma borda.
  const borda = new Uint8Array(l * a);
  const pilha = [];
  for (let i = 0; i < nms.length; i++) {
    if (nms[i] >= alto) {
      borda[i] = 1;
      pilha.push(i);
    }
  }
  while (pilha.length) {
    const i = pilha.pop();
    const x = i % l;
    const y = (i - x) / l;
    for (let dy = -1; dy <= 1; dy++) {
      for (let dx = -1; dx <= 1; dx++) {
        const xx = x + dx;
        const yy = y + dy;
        if (xx < 0 || yy < 0 || xx >= l || yy >= a) continue;
        const j = yy * l + xx;
        if (!borda[j] && nms[j] >= baixo) {
          borda[j] = 1;
          pilha.push(j);
        }
      }
    }
  }
  return deCinza(l, a, Array.from(borda, (b) => (b ? 255 : 0)));
}
