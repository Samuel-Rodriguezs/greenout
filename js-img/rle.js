import { criar } from './imagem.js';

// RLE de bytes: pares [contagem 1..255, valor].
export function codificarRLE(bytes) {
  const out = [];
  for (let i = 0; i < bytes.length; ) {
    let n = 1;
    while (i + n < bytes.length && bytes[i + n] === bytes[i] && n < 255) n++;
    out.push(n, bytes[i]);
    i += n;
  }
  return Uint8Array.from(out);
}

export function decodificarRLE(codigo) {
  if (codigo.length % 2) throw new Error('RLE com tamanho ímpar');
  const out = [];
  for (let i = 0; i < codigo.length; i += 2) {
    if (codigo[i] === 0) throw new Error('contagem zero');
    for (let k = 0; k < codigo[i]; k++) out.push(codigo[i + 1]);
  }
  return Uint8Array.from(out);
}

// Runs por linha de uma imagem binária (R >= 128 = 1): lista de {valor, comprimento} por linha.
export function runsPorLinha(img) {
  const linhas = [];
  for (let y = 0; y < img.altura; y++) {
    const runs = [];
    for (let x = 0; x < img.largura; x++) {
      const v = img.dados[(y * img.largura + x) * 4] >= 128 ? 1 : 0;
      const ult = runs[runs.length - 1];
      if (ult && ult.valor === v) ult.comprimento++;
      else runs.push({ valor: v, comprimento: 1 });
    }
    linhas.push(runs);
  }
  return linhas;
}

export function deRuns(largura, linhas) {
  const img = criar(largura, linhas.length);
  linhas.forEach((runs, y) => {
    let x = 0;
    for (const { valor, comprimento } of runs) {
      for (let k = 0; k < comprimento; k++, x++) {
        if (x >= largura) throw new RangeError('runs excedem a largura');
        const o = (y * largura + x) * 4;
        const c = valor ? 255 : 0;
        img.dados[o] = c;
        img.dados[o + 1] = c;
        img.dados[o + 2] = c;
      }
    }
    if (x !== largura) throw new RangeError('runs não cobrem a largura');
  });
  return img;
}

// Compressão de uma imagem inteira: RLE do plano R (varredura por linhas).
export function rleImagem(img) {
  const plano = new Uint8Array(img.largura * img.altura);
  for (let i = 0; i < plano.length; i++) plano[i] = img.dados[i * 4];
  return codificarRLE(plano);
}
