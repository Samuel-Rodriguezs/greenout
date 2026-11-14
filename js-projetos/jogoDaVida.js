// Jogo da Vida de Conway em grade finita (células fora da borda são mortas).

export function criarGrade(linhas, colunas, vivas = []) {
  if (!Number.isInteger(linhas) || !Number.isInteger(colunas) || linhas < 1 || colunas < 1) {
    throw new RangeError('Dimensões inválidas');
  }
  const grade = Array.from({ length: linhas }, () => Array(colunas).fill(false));
  for (const [l, c] of vivas) {
    if (l < 0 || l >= linhas || c < 0 || c >= colunas) {
      throw new RangeError(`Célula fora da grade: ${l},${c}`);
    }
    grade[l][c] = true;
  }
  return grade;
}

export function contarVizinhas(grade, l, c) {
  let total = 0;
  for (let dl = -1; dl <= 1; dl++) {
    for (let dc = -1; dc <= 1; dc++) {
      if (dl === 0 && dc === 0) continue;
      if (grade[l + dl]?.[c + dc]) total++;
    }
  }
  return total;
}

export function proximaGeracao(grade) {
  return grade.map((linha, l) =>
    linha.map((viva, c) => {
      const n = contarVizinhas(grade, l, c);
      return viva ? n === 2 || n === 3 : n === 3;
    }),
  );
}

export function simular(grade, geracoes) {
  let atual = grade;
  for (let i = 0; i < geracoes; i++) atual = proximaGeracao(atual);
  return atual;
}

export function paraTexto(grade) {
  return grade.map((linha) => linha.map((v) => (v ? '#' : '.')).join('')).join('\n');
}

export function deTexto(texto) {
  return texto
    .trim()
    .split('\n')
    .map((linha) => [...linha.trim()].map((ch) => ch === '#'));
}

export function populacao(grade) {
  return grade.flat().filter(Boolean).length;
}
