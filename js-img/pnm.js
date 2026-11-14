import { criar } from './imagem.js';
import { planoLuma } from './cinza.js';

const enc = new TextEncoder();

// PPM binário (P6): RGB 8 bits, alfa descartado.
export function codificarPPM(img) {
  const cab = enc.encode(`P6\n${img.largura} ${img.altura}\n255\n`);
  const out = new Uint8Array(cab.length + img.largura * img.altura * 3);
  out.set(cab);
  let o = cab.length;
  for (let i = 0; i < img.largura * img.altura; i++) {
    out[o++] = img.dados[i * 4];
    out[o++] = img.dados[i * 4 + 1];
    out[o++] = img.dados[i * 4 + 2];
  }
  return out;
}

// PGM binário (P5): luma BT.601 arredondada.
export function codificarPGM(img) {
  const cab = enc.encode(`P5\n${img.largura} ${img.altura}\n255\n`);
  const out = new Uint8Array(cab.length + img.largura * img.altura);
  out.set(cab);
  const l = planoLuma(img);
  for (let i = 0; i < l.length; i++) out[cab.length + i] = Math.round(l[i]);
  return out;
}

// Lê P2, P3, P5 e P6 (maxval <= 255), com comentários '#'.
export function decodificarPNM(bytes) {
  let pos = 0;
  const ehEspaco = (b) => b === 32 || (b >= 9 && b <= 13);
  const token = () => {
    for (;;) {
      while (pos < bytes.length && ehEspaco(bytes[pos])) pos++;
      if (bytes[pos] !== 35) break;
      while (pos < bytes.length && bytes[pos] !== 10) pos++;
    }
    const ini = pos;
    while (pos < bytes.length && !ehEspaco(bytes[pos])) pos++;
    if (ini === pos) throw new Error('PNM truncado');
    return String.fromCharCode(...bytes.subarray(ini, pos));
  };
  const magico = token();
  if (!['P2', 'P3', 'P5', 'P6'].includes(magico)) throw new Error(`formato não suportado: ${magico}`);
  const largura = Number(token());
  const altura = Number(token());
  const maxval = Number(token());
  if (!(maxval > 0 && maxval <= 255)) throw new Error('maxval não suportado');
  const canais = magico === 'P3' || magico === 'P6' ? 3 : 1;
  const img = criar(largura, altura);
  const total = largura * altura * canais;
  const escala = 255 / maxval;
  const valores = new Array(total);
  if (magico === 'P5' || magico === 'P6') {
    pos++; // um único espaço após o maxval
    if (bytes.length - pos < total) throw new Error('PNM truncado');
    for (let i = 0; i < total; i++) valores[i] = bytes[pos + i];
  } else {
    for (let i = 0; i < total; i++) valores[i] = Number(token());
  }
  for (let i = 0; i < largura * altura; i++) {
    for (let c = 0; c < 3; c++) {
      img.dados[i * 4 + c] = Math.round(valores[i * canais + (canais === 3 ? c : 0)] * escala);
    }
  }
  return img;
}
