import { criar, clonar } from './imagem.js';

const INDICE = { r: 0, g: 1, b: 2, a: 3 };

function canalIdx(c) {
  const i = typeof c === 'number' ? c : INDICE[c];
  if (i === undefined || i < 0 || i > 3) throw new Error(`canal inválido: ${c}`);
  return i;
}

// Imagem em cinza com o valor do canal escolhido.
export function extrairCanal(img, canal) {
  const c = canalIdx(canal);
  const s = criar(img.largura, img.altura);
  for (let i = 0; i < img.largura * img.altura; i++) {
    const v = img.dados[i * 4 + c];
    s.dados.set([v, v, v, 255], i * 4);
  }
  return s;
}

// Mantém só um canal RGB (os outros ficam 0).
export function isolarCanal(img, canal) {
  const c = canalIdx(canal);
  if (c === 3) throw new Error('use extrairCanal para o alfa');
  const s = clonar(img);
  for (let i = 0; i < img.largura * img.altura; i++) {
    for (let k = 0; k < 3; k++) if (k !== c) s.dados[i * 4 + k] = 0;
  }
  return s;
}

// Troca a ordem dos canais RGB, p. ex. 'bgr'.
export function trocarCanais(img, ordem) {
  if (!/^[rgb]{3}$/.test(ordem)) throw new Error('ordem deve ter 3 letras de r/g/b');
  const s = clonar(img);
  for (let i = 0; i < img.largura * img.altura; i++) {
    for (let k = 0; k < 3; k++) s.dados[i * 4 + k] = img.dados[i * 4 + INDICE[ordem[k]]];
  }
  return s;
}

// Substitui o canal de `img` pelo cinza de `fonte` (mesmo tamanho).
export function definirCanal(img, canal, fonte) {
  const c = canalIdx(canal);
  if (img.largura !== fonte.largura || img.altura !== fonte.altura) throw new RangeError('tamanhos diferentes');
  const s = clonar(img);
  for (let i = 0; i < img.largura * img.altura; i++) s.dados[i * 4 + c] = fonte.dados[i * 4];
  return s;
}

// Mistura linear: (1-t)*a + t*b.
export function misturar(a, b, t) {
  if (a.largura !== b.largura || a.altura !== b.altura) throw new RangeError('tamanhos diferentes');
  const s = criar(a.largura, a.altura);
  for (let i = 0; i < a.dados.length; i++) s.dados[i] = (1 - t) * a.dados[i] + t * b.dados[i];
  return s;
}

// Composição "source over" com alfa (frente sobre fundo), mesmo tamanho; `opacidade` extra 0..1.
export function alphaBlend(fundo, frente, opacidade = 1) {
  if (fundo.largura !== frente.largura || fundo.altura !== frente.altura) throw new RangeError('tamanhos diferentes');
  const s = criar(fundo.largura, fundo.altura);
  for (let i = 0; i < fundo.largura * fundo.altura; i++) {
    const o = i * 4;
    const af = (frente.dados[o + 3] / 255) * opacidade;
    const ab = fundo.dados[o + 3] / 255;
    const ao = af + ab * (1 - af);
    for (let k = 0; k < 3; k++) {
      const v = ao === 0 ? 0 : (frente.dados[o + k] * af + fundo.dados[o + k] * ab * (1 - af)) / ao;
      s.dados[o + k] = v;
    }
    s.dados[o + 3] = ao * 255;
  }
  return s;
}
