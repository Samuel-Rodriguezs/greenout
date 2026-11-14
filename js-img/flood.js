import { clonar, dentro, obter, definir } from './imagem.js';

// Flood fill (balde de tinta) por varredura de linhas.
// tolerancia: diferença máxima por canal RGBA em relação à cor da semente.
// Retorna { imagem, preenchidos }; a imagem de entrada não é alterada.
export function preencher(img, x, y, cor, { tolerancia = 0, conectividade = 4 } = {}) {
  if (!dentro(img, x, y)) throw new RangeError('semente fora da imagem');
  if (conectividade !== 4 && conectividade !== 8) throw new Error('conectividade deve ser 4 ou 8');
  const alvo = obter(img, x, y);
  const saida = clonar(img);
  const visitado = new Uint8Array(img.largura * img.altura);
  const casa = (px, py) => {
    const i = (py * img.largura + px) * 4;
    for (let c = 0; c < 4; c++) if (Math.abs(img.dados[i + c] - alvo[c]) > tolerancia) return false;
    return true;
  };
  const pilha = [[x, y]];
  let n = 0;
  while (pilha.length) {
    const [sx, sy] = pilha.pop();
    if (visitado[sy * img.largura + sx] || !casa(sx, sy)) continue;
    let x0 = sx;
    let x1 = sx;
    while (x0 > 0 && !visitado[sy * img.largura + x0 - 1] && casa(x0 - 1, sy)) x0--;
    while (x1 < img.largura - 1 && !visitado[sy * img.largura + x1 + 1] && casa(x1 + 1, sy)) x1++;
    for (let px = x0; px <= x1; px++) {
      visitado[sy * img.largura + px] = 1;
      definir(saida, px, sy, cor);
      n++;
    }
    const ext = conectividade === 8 ? 1 : 0;
    for (const py of [sy - 1, sy + 1]) {
      if (py < 0 || py >= img.altura) continue;
      for (let px = Math.max(0, x0 - ext); px <= Math.min(img.largura - 1, x1 + ext); px++) {
        if (!visitado[py * img.largura + px] && casa(px, py)) pilha.push([px, py]);
      }
    }
  }
  return { imagem: saida, preenchidos: n };
}
