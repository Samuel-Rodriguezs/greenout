// Imagem = { largura, altura, dados: Uint8ClampedArray RGBA }

export function criar(largura, altura, cor = [0, 0, 0, 255]) {
  if (!Number.isInteger(largura) || !Number.isInteger(altura) || largura < 1 || altura < 1) {
    throw new RangeError('dimensões inválidas');
  }
  const dados = new Uint8ClampedArray(largura * altura * 4);
  for (let i = 0; i < dados.length; i += 4) {
    dados[i] = cor[0];
    dados[i + 1] = cor[1];
    dados[i + 2] = cor[2];
    dados[i + 3] = cor[3] ?? 255;
  }
  return { largura, altura, dados };
}

// Cria imagem a partir de uma lista de pixels [r,g,b,a?] em ordem de linha.
export function dePixels(largura, altura, pixels) {
  if (pixels.length !== largura * altura) throw new RangeError('quantidade de pixels incorreta');
  const img = criar(largura, altura);
  pixels.forEach((p, i) => {
    img.dados.set([p[0], p[1], p[2], p[3] ?? 255], i * 4);
  });
  return img;
}

// Imagem em tons de cinza (R=G=B) a partir de valores 0..255.
export function deCinza(largura, altura, valores) {
  if (valores.length !== largura * altura) throw new RangeError('quantidade de valores incorreta');
  const img = criar(largura, altura);
  for (let i = 0; i < valores.length; i++) {
    const v = valores[i];
    img.dados[i * 4] = v;
    img.dados[i * 4 + 1] = v;
    img.dados[i * 4 + 2] = v;
  }
  return img;
}

export function dentro(img, x, y) {
  return Number.isInteger(x) && Number.isInteger(y) && x >= 0 && y >= 0 && x < img.largura && y < img.altura;
}

export function obter(img, x, y) {
  if (!dentro(img, x, y)) throw new RangeError(`pixel fora da imagem: (${x}, ${y})`);
  const i = (y * img.largura + x) * 4;
  return [img.dados[i], img.dados[i + 1], img.dados[i + 2], img.dados[i + 3]];
}

export function definir(img, x, y, cor) {
  if (!dentro(img, x, y)) throw new RangeError(`pixel fora da imagem: (${x}, ${y})`);
  const i = (y * img.largura + x) * 4;
  img.dados[i] = cor[0];
  img.dados[i + 1] = cor[1];
  img.dados[i + 2] = cor[2];
  img.dados[i + 3] = cor[3] ?? 255;
}

// Índice 1D tratando bordas: 'clamp' | 'wrap' | 'espelho' | 'zero' (devolve -1).
export function indiceBorda(i, n, modo = 'clamp') {
  if (i >= 0 && i < n) return i;
  switch (modo) {
    case 'clamp':
      return i < 0 ? 0 : n - 1;
    case 'wrap':
      return ((i % n) + n) % n;
    case 'espelho': {
      const m = ((i % (2 * n)) + 2 * n) % (2 * n);
      return m < n ? m : 2 * n - 1 - m;
    }
    case 'zero':
      return -1;
    default:
      throw new Error(`modo de borda desconhecido: ${modo}`);
  }
}

export function obterBorda(img, x, y, modo = 'clamp') {
  const xi = indiceBorda(x, img.largura, modo);
  const yi = indiceBorda(y, img.altura, modo);
  if (xi < 0 || yi < 0) return [0, 0, 0, 0];
  return obter(img, xi, yi);
}

export function clonar(img) {
  return { largura: img.largura, altura: img.altura, dados: new Uint8ClampedArray(img.dados) };
}

export function igual(a, b) {
  if (a.largura !== b.largura || a.altura !== b.altura) return false;
  for (let i = 0; i < a.dados.length; i++) if (a.dados[i] !== b.dados[i]) return false;
  return true;
}

// Plano float de um canal (0=R,1=G,2=B,3=A).
export function plano(img, canal) {
  const p = new Float64Array(img.largura * img.altura);
  for (let i = 0; i < p.length; i++) p[i] = img.dados[i * 4 + canal];
  return p;
}

// Monta imagem de três planos RGB; alfa copiado de `base` (ou 255).
export function dePlanos(largura, altura, r, g, b, base = null) {
  const img = criar(largura, altura);
  for (let i = 0; i < largura * altura; i++) {
    img.dados[i * 4] = r[i];
    img.dados[i * 4 + 1] = g[i];
    img.dados[i * 4 + 2] = b[i];
    img.dados[i * 4 + 3] = base ? base.dados[i * 4 + 3] : 255;
  }
  return img;
}

// Aplica f(plano, canal) em R, G e B, preservando o alfa.
export function porCanal(img, f) {
  const [r, g, b] = [0, 1, 2].map((c) => f(plano(img, c), c));
  return dePlanos(img.largura, img.altura, r, g, b, img);
}
