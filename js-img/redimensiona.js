import { criar } from './imagem.js';

const grampo = (v, n) => Math.min(n - 1, Math.max(0, v));

// Mapeia a coordenada do destino ao centro do pixel de origem.
const origem = (d, nd, no) => ((d + 0.5) * no) / nd - 0.5;

function validar(l, a) {
  if (!Number.isInteger(l) || !Number.isInteger(a) || l < 1 || a < 1) throw new RangeError('tamanho inválido');
}

export function vizinhoMaisProximo(img, nl, na) {
  validar(nl, na);
  const s = criar(nl, na);
  for (let y = 0; y < na; y++) {
    const sy = grampo(Math.floor(origem(y, na, img.altura) + 0.5), img.altura);
    for (let x = 0; x < nl; x++) {
      const sx = grampo(Math.floor(origem(x, nl, img.largura) + 0.5), img.largura);
      const i = (sy * img.largura + sx) * 4;
      s.dados.set(img.dados.subarray(i, i + 4), (y * nl + x) * 4);
    }
  }
  return s;
}

export function bilinear(img, nl, na) {
  validar(nl, na);
  const s = criar(nl, na);
  const L = img.largura;
  for (let y = 0; y < na; y++) {
    const fy = origem(y, na, img.altura);
    const y0 = Math.floor(fy);
    const ty = fy - y0;
    for (let x = 0; x < nl; x++) {
      const fx = origem(x, nl, L);
      const x0 = Math.floor(fx);
      const tx = fx - x0;
      for (let c = 0; c < 4; c++) {
        const p = (xx, yy) => img.dados[(grampo(yy, img.altura) * L + grampo(xx, L)) * 4 + c];
        const topo = p(x0, y0) * (1 - tx) + p(x0 + 1, y0) * tx;
        const base = p(x0, y0 + 1) * (1 - tx) + p(x0 + 1, y0 + 1) * tx;
        s.dados[(y * nl + x) * 4 + c] = topo * (1 - ty) + base * ty;
      }
    }
  }
  return s;
}

// Pesos de Catmull-Rom (a = -0.5) para t em [0,1) sobre 4 amostras.
export function pesosCubicos(t) {
  const a = -0.5;
  const w = (d) => {
    d = Math.abs(d);
    if (d <= 1) return (a + 2) * d ** 3 - (a + 3) * d ** 2 + 1;
    if (d < 2) return a * d ** 3 - 5 * a * d ** 2 + 8 * a * d - 4 * a;
    return 0;
  };
  return [w(1 + t), w(t), w(1 - t), w(2 - t)];
}

export function bicubico(img, nl, na) {
  validar(nl, na);
  const s = criar(nl, na);
  const L = img.largura;
  for (let y = 0; y < na; y++) {
    const fy = origem(y, na, img.altura);
    const y0 = Math.floor(fy);
    const wy = pesosCubicos(fy - y0);
    for (let x = 0; x < nl; x++) {
      const fx = origem(x, nl, L);
      const x0 = Math.floor(fx);
      const wx = pesosCubicos(fx - x0);
      for (let c = 0; c < 4; c++) {
        let acc = 0;
        for (let j = 0; j < 4; j++) {
          const yy = grampo(y0 - 1 + j, img.altura);
          let linha = 0;
          for (let i = 0; i < 4; i++) linha += wx[i] * img.dados[(yy * L + grampo(x0 - 1 + i, L)) * 4 + c];
          acc += wy[j] * linha;
        }
        s.dados[(y * nl + x) * 4 + c] = acc;
      }
    }
  }
  return s;
}
