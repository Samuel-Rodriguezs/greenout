// 2048: deslizar e fundir peças em grade quadrada.

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

export function criarGrade(n = 4) {
  return Array.from({ length: n }, () => Array(n).fill(0));
}

/** Insere uma peça (2 com 90%, 4 com 10%) numa célula vazia aleatória. */
export function adicionarPeca(grade, rng) {
  const vazias = [];
  grade.forEach((linha, l) => linha.forEach((v, c) => v === 0 && vazias.push([l, c])));
  if (vazias.length === 0) return grade;
  const [l, c] = vazias[Math.floor(rng() * vazias.length)];
  const nova = grade.map((x) => x.slice());
  nova[l][c] = rng() < 0.9 ? 2 : 4;
  return nova;
}

export function novoJogo(rng, n = 4) {
  let g = criarGrade(n);
  g = adicionarPeca(g, rng);
  g = adicionarPeca(g, rng);
  return { grade: g, pontos: 0 };
}

/** Desliza uma linha para a esquerda; cada peça funde no máximo uma vez. */
export function deslizarLinha(linha) {
  const nums = linha.filter((v) => v !== 0);
  const saida = [];
  let pontos = 0;
  for (let i = 0; i < nums.length; i++) {
    if (nums[i] === nums[i + 1]) {
      saida.push(nums[i] * 2);
      pontos += nums[i] * 2;
      i++;
    } else saida.push(nums[i]);
  }
  while (saida.length < linha.length) saida.push(0);
  return { linha: saida, pontos };
}

function transpor(g) {
  return g.map((_, c) => g.map((linha) => linha[c]));
}

/** Move a grade; direções: 'esquerda' | 'direita' | 'cima' | 'baixo'. Não adiciona peça. */
export function mover(grade, direcao) {
  let g = grade;
  const vertical = direcao === 'cima' || direcao === 'baixo';
  const inverter = direcao === 'direita' || direcao === 'baixo';
  if (!['esquerda', 'direita', 'cima', 'baixo'].includes(direcao)) throw new Error('direção inválida');
  if (vertical) g = transpor(g);
  let pontos = 0;
  g = g.map((linha) => {
    const base = inverter ? linha.slice().reverse() : linha;
    const r = deslizarLinha(base);
    pontos += r.pontos;
    return inverter ? r.linha.reverse() : r.linha;
  });
  if (vertical) g = transpor(g);
  const moveu = g.some((linha, l) => linha.some((v, c) => v !== grade[l][c]));
  return { grade: g, pontos, moveu };
}

/** Jogada completa: move e, se algo mudou, adiciona nova peça. */
export function jogar(estado, direcao, rng) {
  const r = mover(estado.grade, direcao);
  if (!r.moveu) return estado;
  return { grade: adicionarPeca(r.grade, rng), pontos: estado.pontos + r.pontos };
}

export function fimDeJogo(grade) {
  return ['esquerda', 'direita', 'cima', 'baixo'].every((d) => !mover(grade, d).moveu);
}

export function venceu(grade, alvo = 2048) {
  return grade.some((l) => l.some((v) => v >= alvo));
}
