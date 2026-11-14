import { deCinza } from './imagem.js';

// Elementos estruturantes: listas de deslocamentos [dx, dy].
export function quadrado(raio = 1) {
  const e = [];
  for (let dy = -raio; dy <= raio; dy++) for (let dx = -raio; dx <= raio; dx++) e.push([dx, dy]);
  return e;
}

export function cruz(raio = 1) {
  const e = [[0, 0]];
  for (let r = 1; r <= raio; r++) e.push([r, 0], [-r, 0], [0, r], [0, -r]);
  return e;
}

// Binariza: primeiro plano = canal R >= 128. Fora da imagem conta como fundo.
function binario(img) {
  const b = new Uint8Array(img.largura * img.altura);
  for (let i = 0; i < b.length; i++) b[i] = img.dados[i * 4] >= 128 ? 1 : 0;
  return b;
}

const paraImagem = (b, l, a) => deCinza(l, a, Array.from(b, (v) => (v ? 255 : 0)));

function aplicar(img, el, erodir) {
  const l = img.largura;
  const a = img.altura;
  const b = binario(img);
  const out = new Uint8Array(b.length);
  for (let y = 0; y < a; y++) {
    for (let x = 0; x < l; x++) {
      let ok = erodir; // erosão: todos 1; dilatação: algum 1
      for (const [dx, dy] of el) {
        const xx = x + dx;
        const yy = y + dy;
        const v = xx < 0 || yy < 0 || xx >= l || yy >= a ? 0 : b[yy * l + xx];
        if (erodir && !v) {
          ok = false;
          break;
        }
        if (!erodir && v) {
          ok = true;
          break;
        }
      }
      out[y * l + x] = ok ? 1 : 0;
    }
  }
  return paraImagem(out, l, a);
}

export const erosao = (img, el = quadrado(1)) => aplicar(img, el, true);
export const dilatacao = (img, el = quadrado(1)) => aplicar(img, el, false);
export const abertura = (img, el = quadrado(1)) => dilatacao(erosao(img, el), el);
export const fechamento = (img, el = quadrado(1)) => erosao(dilatacao(img, el), el);

// Gradiente morfológico: dilatação - erosão (contorno).
export function gradienteMorfologico(img, el = quadrado(1)) {
  const d = dilatacao(img, el);
  const e = erosao(img, el);
  return deCinza(img.largura, img.altura, Array.from({ length: img.largura * img.altura }, (_, i) => d.dados[i * 4] - e.dados[i * 4]));
}
