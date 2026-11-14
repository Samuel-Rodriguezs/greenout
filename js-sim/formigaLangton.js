// Formiga de Langton em grade toroidal.
// Direções: 0 = cima, 1 = direita, 2 = baixo, 3 = esquerda.

const DX = [0, 1, 0, -1];
const DY = [-1, 0, 1, 0];

export function criarFormiga(largura, altura, x = Math.floor(largura / 2), y = Math.floor(altura / 2), dir = 0) {
  return {
    largura, altura, x, y, dir, passos: 0,
    grade: Array.from({ length: altura }, () => Array(largura).fill(0)),
  };
}

/** Um passo: célula branca (0) -> vira à direita; preta (1) -> à esquerda; inverte a cor e avança. */
export function passo(f) {
  const atual = f.grade[f.y][f.x];
  f.dir = (f.dir + (atual === 0 ? 1 : 3)) % 4;
  f.grade[f.y][f.x] = 1 - atual;
  f.x = (f.x + DX[f.dir] + f.largura) % f.largura;
  f.y = (f.y + DY[f.dir] + f.altura) % f.altura;
  f.passos++;
  return f;
}

export function simular(f, n) {
  for (let i = 0; i < n; i++) passo(f);
  return f;
}

export function contarPretas(f) {
  return f.grade.reduce((s, l) => s + l.reduce((a, v) => a + v, 0), 0);
}

export function renderizar(f) {
  return f.grade.map((l, y) => l.map((v, x) => (x === f.x && y === f.y ? '@' : v ? '#' : '.')).join('')).join('\n');
}
