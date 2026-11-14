import { criar } from './imagem.js';

// Median cut: devolve até n cores [r,g,b], ordenadas por luma.
export function medianCut(img, n) {
  if (!Number.isInteger(n) || n < 1) throw new RangeError('n deve ser inteiro >= 1');
  const pixels = [];
  for (let i = 0; i < img.largura * img.altura; i++) pixels.push([img.dados[i * 4], img.dados[i * 4 + 1], img.dados[i * 4 + 2]]);
  const faixa = (caixa) => {
    let melhor = { canal: 0, tam: -1 };
    for (let c = 0; c < 3; c++) {
      let min = 255;
      let max = 0;
      for (const p of caixa) {
        min = Math.min(min, p[c]);
        max = Math.max(max, p[c]);
      }
      if (max - min > melhor.tam) melhor = { canal: c, tam: max - min };
    }
    return melhor;
  };
  let caixas = [pixels];
  while (caixas.length < n) {
    // escolhe a caixa com maior faixa de cor que ainda possa ser dividida
    let alvo = -1;
    let alvoFaixa = { canal: 0, tam: 0 };
    caixas.forEach((c, i) => {
      const f = faixa(c);
      if (f.tam > alvoFaixa.tam) {
        alvo = i;
        alvoFaixa = f;
      }
    });
    if (alvo < 0) break;
    const caixa = caixas[alvo].slice().sort((p, q) => p[alvoFaixa.canal] - q[alvoFaixa.canal]);
    const meio = caixa.length >> 1;
    caixas.splice(alvo, 1, caixa.slice(0, meio), caixa.slice(meio));
  }
  return caixas
    .map((c) => [0, 1, 2].map((k) => Math.round(c.reduce((s, p) => s + p[k], 0) / c.length)))
    .sort((p, q) => 0.299 * p[0] + 0.587 * p[1] + 0.114 * p[2] - (0.299 * q[0] + 0.587 * q[1] + 0.114 * q[2]));
}

export function maisProxima(paleta, r, g, b) {
  let melhor = 0;
  let d = Infinity;
  paleta.forEach((c, i) => {
    const dd = (c[0] - r) ** 2 + (c[1] - g) ** 2 + (c[2] - b) ** 2;
    if (dd < d) {
      d = dd;
      melhor = i;
    }
  });
  return melhor;
}

export function aplicarPaleta(img, paleta) {
  const s = criar(img.largura, img.altura);
  for (let i = 0; i < img.largura * img.altura; i++) {
    const c = paleta[maisProxima(paleta, img.dados[i * 4], img.dados[i * 4 + 1], img.dados[i * 4 + 2])];
    s.dados.set([c[0], c[1], c[2], img.dados[i * 4 + 3]], i * 4);
  }
  return s;
}

export const quantizar = (img, n) => aplicarPaleta(img, medianCut(img, n));
