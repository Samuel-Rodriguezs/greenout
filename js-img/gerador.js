import { criar } from './imagem.js';

const mistura = (a, b, t) => a.map((v, i) => Math.round(v + (b[i] - v) * t));

// Gradiente linear horizontal: cor1 na coluna 0, cor2 na última.
export function gradienteHorizontal(largura, altura, c1, c2) {
  const img = criar(largura, altura);
  for (let x = 0; x < largura; x++) {
    const c = mistura(c1, c2, largura === 1 ? 0 : x / (largura - 1));
    for (let y = 0; y < altura; y++) img.dados.set([c[0], c[1], c[2], 255], (y * largura + x) * 4);
  }
  return img;
}

export function gradienteVertical(largura, altura, c1, c2) {
  const img = criar(largura, altura);
  for (let y = 0; y < altura; y++) {
    const c = mistura(c1, c2, altura === 1 ? 0 : y / (altura - 1));
    for (let x = 0; x < largura; x++) img.dados.set([c[0], c[1], c[2], 255], (y * largura + x) * 4);
  }
  return img;
}

// Gradiente radial: c1 no centro, c2 a partir da distância máxima até o canto.
export function gradienteRadial(largura, altura, c1, c2) {
  const img = criar(largura, altura);
  const cx = (largura - 1) / 2;
  const cy = (altura - 1) / 2;
  const maximo = Math.hypot(cx, cy) || 1;
  for (let y = 0; y < altura; y++) {
    for (let x = 0; x < largura; x++) {
      const c = mistura(c1, c2, Math.min(1, Math.hypot(x - cx, y - cy) / maximo));
      img.dados.set([c[0], c[1], c[2], 255], (y * largura + x) * 4);
    }
  }
  return img;
}

// Tabuleiro com casas de `tam` pixels; a casa (0,0) usa c1.
export function xadrez(largura, altura, tam, c1 = [255, 255, 255], c2 = [0, 0, 0]) {
  if (!Number.isInteger(tam) || tam < 1) throw new RangeError('tam inválido');
  const img = criar(largura, altura);
  for (let y = 0; y < altura; y++) {
    for (let x = 0; x < largura; x++) {
      const c = (Math.floor(x / tam) + Math.floor(y / tam)) % 2 === 0 ? c1 : c2;
      img.dados.set([c[0], c[1], c[2], 255], (y * largura + x) * 4);
    }
  }
  return img;
}

export function listras(largura, altura, tam, c1 = [255, 255, 255], c2 = [0, 0, 0]) {
  if (!Number.isInteger(tam) || tam < 1) throw new RangeError('tam inválido');
  const img = criar(largura, altura);
  for (let y = 0; y < altura; y++) {
    for (let x = 0; x < largura; x++) {
      const c = Math.floor(x / tam) % 2 === 0 ? c1 : c2;
      img.dados.set([c[0], c[1], c[2], 255], (y * largura + x) * 4);
    }
  }
  return img;
}

// PRNG mulberry32: determinístico a partir da semente; retorna floats em [0,1).
export function prng(semente) {
  let s = semente >>> 0;
  return () => {
    s = (s + 0x6d2b79f5) >>> 0;
    let t = s;
    t = Math.imul(t ^ (t >>> 15), t | 1);
    t ^= t + Math.imul(t ^ (t >>> 7), t | 61);
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}

// Ruído uniforme; `cinza` gera R=G=B.
export function ruido(largura, altura, semente, cinza = true) {
  const rnd = prng(semente);
  const img = criar(largura, altura);
  for (let i = 0; i < largura * altura; i++) {
    const r = Math.floor(rnd() * 256);
    if (cinza) img.dados.set([r, r, r, 255], i * 4);
    else img.dados.set([r, Math.floor(rnd() * 256), Math.floor(rnd() * 256), 255], i * 4);
  }
  return img;
}
