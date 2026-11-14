// Gerador de dungeon por BSP (Binary Space Partitioning). 1 = chão, 0 = parede.

export function mulberry32(seed) {
  let a = seed >>> 0;
  return () => {
    a = (a + 0x6d2b79f5) >>> 0;
    let t = a;
    t = Math.imul(t ^ (t >>> 15), t | 1);
    t ^= t + Math.imul(t ^ (t >>> 7), t | 61);
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}

const inteiro = (rng, min, max) => min + Math.floor(rng() * (max - min + 1));

/** Divide recursivamente a área; cada nó: {x,y,w,h,esq,dir,sala}. */
function dividir(no, rng, minLado, profundidade) {
  if (profundidade === 0) return;
  const podeH = no.w >= minLado * 2 + 1; // corte vertical (divide a largura)
  const podeV = no.h >= minLado * 2 + 1;
  if (!podeH && !podeV) return;
  let horizontal; // true: divide a largura
  if (podeH && podeV) horizontal = no.w / no.h > 1.25 ? true : no.h / no.w > 1.25 ? false : rng() < 0.5;
  else horizontal = podeH;
  if (horizontal) {
    const corte = inteiro(rng, minLado, no.w - minLado - 1);
    no.esq = { x: no.x, y: no.y, w: corte, h: no.h };
    no.dir = { x: no.x + corte + 1, y: no.y, w: no.w - corte - 1, h: no.h };
  } else {
    const corte = inteiro(rng, minLado, no.h - minLado - 1);
    no.esq = { x: no.x, y: no.y, w: no.w, h: corte };
    no.dir = { x: no.x, y: no.y + corte + 1, w: no.w, h: no.h - corte - 1 };
  }
  dividir(no.esq, rng, minLado, profundidade - 1);
  dividir(no.dir, rng, minLado, profundidade - 1);
}

function criarSalas(no, rng, minSala, salas) {
  if (no.esq) {
    criarSalas(no.esq, rng, minSala, salas);
    criarSalas(no.dir, rng, minSala, salas);
    return;
  }
  const w = inteiro(rng, Math.min(minSala, no.w), no.w);
  const h = inteiro(rng, Math.min(minSala, no.h), no.h);
  const x = no.x + inteiro(rng, 0, no.w - w);
  const y = no.y + inteiro(rng, 0, no.h - h);
  no.sala = { x, y, w, h };
  salas.push(no.sala);
}

function centro(s) {
  return [s.x + Math.floor(s.w / 2), s.y + Math.floor(s.h / 2)];
}

function salaDe(no, rng) {
  if (!no.esq) return no.sala;
  return salaDe(rng() < 0.5 ? no.esq : no.dir, rng);
}

function corredor(grade, a, b, rng) {
  let [x, y] = a;
  const [x2, y2] = b;
  const horizontalPrimeiro = rng() < 0.5;
  const andarX = () => { while (x !== x2) { grade[y][x] = 1; x += Math.sign(x2 - x); } };
  const andarY = () => { while (y !== y2) { grade[y][x] = 1; y += Math.sign(y2 - y); } };
  if (horizontalPrimeiro) { andarX(); andarY(); } else { andarY(); andarX(); }
  grade[y][x] = 1;
}

function conectar(no, grade, rng) {
  if (!no.esq) return;
  conectar(no.esq, grade, rng);
  conectar(no.dir, grade, rng);
  corredor(grade, centro(salaDe(no.esq, rng)), centro(salaDe(no.dir, rng)), rng);
}

/**
 * Gera a dungeon. Retorna {grade, salas, largura, altura}.
 * opções: profundidade (padrão 4), minLado (tamanho mínimo de partição, 8), minSala (4).
 */
export function gerar(largura, altura, rng, { profundidade = 4, minLado = 8, minSala = 4 } = {}) {
  if (largura < minLado || altura < minLado) throw new Error('mapa pequeno demais');
  const raiz = { x: 1, y: 1, w: largura - 2, h: altura - 2 }; // preserva borda de parede
  dividir(raiz, rng, minLado, profundidade);
  const salas = [];
  criarSalas(raiz, rng, minSala, salas);
  const grade = Array.from({ length: altura }, () => Array(largura).fill(0));
  for (const s of salas) for (let y = s.y; y < s.y + s.h; y++) for (let x = s.x; x < s.x + s.w; x++) grade[y][x] = 1;
  conectar(raiz, grade, rng);
  return { grade, salas, largura, altura };
}

/** Quantidade de células de chão alcançáveis a partir de (x,y) (flood fill 4-direções). */
export function regiaoConexa(grade, x, y) {
  if (!grade[y]?.[x]) return 0;
  const visto = new Set([x + ',' + y]);
  const pilha = [[x, y]];
  while (pilha.length) {
    const [cx, cy] = pilha.pop();
    for (const [dx, dy] of [[1, 0], [-1, 0], [0, 1], [0, -1]]) {
      const nx = cx + dx;
      const ny = cy + dy;
      if (grade[ny]?.[nx] === 1 && !visto.has(nx + ',' + ny)) {
        visto.add(nx + ',' + ny);
        pilha.push([nx, ny]);
      }
    }
  }
  return visto.size;
}

export function renderizar(grade) {
  return grade.map((l) => l.map((v) => (v ? '.' : '#')).join('')).join('\n');
}
