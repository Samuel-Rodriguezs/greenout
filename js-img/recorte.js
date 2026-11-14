import { criar, definir, obter, obterBorda } from './imagem.js';

// Recorta o retângulo (x, y, largura, altura); deve caber na imagem.
export function recortar(img, x, y, largura, altura) {
  if (largura < 1 || altura < 1 || x < 0 || y < 0 || x + largura > img.largura || y + altura > img.altura) {
    throw new RangeError('recorte fora da imagem');
  }
  const s = criar(largura, altura);
  for (let j = 0; j < altura; j++) {
    const ini = ((y + j) * img.largura + x) * 4;
    s.dados.set(img.dados.subarray(ini, ini + largura * 4), j * largura * 4);
  }
  return s;
}

// Adiciona margens. modo: 'constante' (usa `cor`) | 'clamp' | 'wrap' | 'espelho'.
export function acolchoar(img, { topo = 0, direita = 0, baixo = 0, esquerda = 0 }, modo = 'constante', cor = [0, 0, 0, 255]) {
  if ([topo, direita, baixo, esquerda].some((v) => !Number.isInteger(v) || v < 0)) throw new RangeError('margens inválidas');
  const s = criar(img.largura + esquerda + direita, img.altura + topo + baixo, cor);
  for (let y = 0; y < s.altura; y++) {
    for (let x = 0; x < s.largura; x++) {
      const ox = x - esquerda;
      const oy = y - topo;
      if (modo === 'constante') {
        if (ox >= 0 && oy >= 0 && ox < img.largura && oy < img.altura) definir(s, x, y, obter(img, ox, oy));
      } else {
        definir(s, x, y, obterBorda(img, ox, oy, modo));
      }
    }
  }
  return s;
}

// Recorte centralizado de tamanho (largura, altura).
export function recorteCentral(img, largura, altura) {
  return recortar(img, Math.floor((img.largura - largura) / 2), Math.floor((img.altura - altura) / 2), largura, altura);
}

// Remove bordas cuja cor é igual à do canto superior esquerdo.
export function aparar(img) {
  const ref = obter(img, 0, 0);
  const igualRef = (x, y) => obter(img, x, y).every((v, i) => v === ref[i]);
  let x0 = img.largura;
  let y0 = img.altura;
  let x1 = -1;
  let y1 = -1;
  for (let y = 0; y < img.altura; y++) {
    for (let x = 0; x < img.largura; x++) {
      if (!igualRef(x, y)) {
        x0 = Math.min(x0, x);
        x1 = Math.max(x1, x);
        y0 = Math.min(y0, y);
        y1 = Math.max(y1, y);
      }
    }
  }
  if (x1 < 0) return null;
  return recortar(img, x0, y0, x1 - x0 + 1, y1 - y0 + 1);
}
