import { criar } from './imagem.js';

// BMP 24 bits sem compressão (BITMAPINFOHEADER), linhas de baixo para cima, BGR, alinhadas a 4 bytes.
export function codificarBMP(img) {
  const linha = Math.ceil((img.largura * 3) / 4) * 4;
  const tamanhoDados = linha * img.altura;
  const total = 54 + tamanhoDados;
  const buf = new Uint8Array(total);
  const v = new DataView(buf.buffer);
  buf[0] = 0x42;
  buf[1] = 0x4d;
  v.setUint32(2, total, true);
  v.setUint32(10, 54, true); // offset dos pixels
  v.setUint32(14, 40, true); // tamanho do cabeçalho DIB
  v.setInt32(18, img.largura, true);
  v.setInt32(22, img.altura, true);
  v.setUint16(26, 1, true); // planos
  v.setUint16(28, 24, true); // bits por pixel
  v.setUint32(34, tamanhoDados, true);
  v.setInt32(38, 2835, true); // 72 dpi
  v.setInt32(42, 2835, true);
  for (let y = 0; y < img.altura; y++) {
    const o = 54 + (img.altura - 1 - y) * linha;
    for (let x = 0; x < img.largura; x++) {
      const i = (y * img.largura + x) * 4;
      buf[o + x * 3] = img.dados[i + 2];
      buf[o + x * 3 + 1] = img.dados[i + 1];
      buf[o + x * 3 + 2] = img.dados[i];
    }
  }
  return buf;
}

export function decodificarBMP(bytes) {
  if (bytes.length < 54 || bytes[0] !== 0x42 || bytes[1] !== 0x4d) throw new Error('não é um BMP');
  const v = new DataView(bytes.buffer, bytes.byteOffset, bytes.byteLength);
  const offset = v.getUint32(10, true);
  const largura = v.getInt32(18, true);
  let altura = v.getInt32(22, true);
  const bpp = v.getUint16(28, true);
  const compressao = v.getUint32(30, true);
  if (bpp !== 24 || compressao !== 0) throw new Error('somente BMP 24 bits sem compressão');
  const cimaParaBaixo = altura < 0;
  altura = Math.abs(altura);
  const linha = Math.ceil((largura * 3) / 4) * 4;
  if (bytes.length < offset + linha * altura) throw new Error('BMP truncado');
  const img = criar(largura, altura);
  for (let y = 0; y < altura; y++) {
    const o = offset + (cimaParaBaixo ? y : altura - 1 - y) * linha;
    for (let x = 0; x < largura; x++) {
      const i = (y * largura + x) * 4;
      img.dados[i] = bytes[o + x * 3 + 2];
      img.dados[i + 1] = bytes[o + x * 3 + 1];
      img.dados[i + 2] = bytes[o + x * 3];
    }
  }
  return img;
}
