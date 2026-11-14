// Sudoku: parser, validação e solver por backtracking com heurística MRV.

/** Converte string de 81 caracteres ('0' ou '.' = vazio) em grade 9x9. */
export function parse(texto) {
  const s = texto.replace(/\s+/g, '');
  if (!/^[0-9.]{81}$/.test(s)) throw new Error('puzzle deve ter 81 caracteres (0-9 ou .)');
  return Array.from({ length: 9 }, (_, l) => [...s.slice(l * 9, l * 9 + 9)].map((c) => (c === '.' ? 0 : Number(c))));
}

export function formatar(grade) {
  return grade.map((l) => l.join('')).join('');
}

/** Verdadeiro se v pode ser colocado em (l,c) sem conflito. */
export function podeColocar(grade, l, c, v) {
  for (let i = 0; i < 9; i++) {
    if (grade[l][i] === v || grade[i][c] === v) return false;
  }
  const bl = l - (l % 3);
  const bc = c - (c % 3);
  for (let i = 0; i < 3; i++) for (let j = 0; j < 3; j++) if (grade[bl + i][bc + j] === v) return false;
  return true;
}

/** Verifica se não há duplicatas nas peças já preenchidas. */
export function gradeConsistente(grade) {
  for (let l = 0; l < 9; l++) {
    for (let c = 0; c < 9; c++) {
      const v = grade[l][c];
      if (!v) continue;
      grade[l][c] = 0;
      const ok = podeColocar(grade, l, c, v);
      grade[l][c] = v;
      if (!ok) return false;
    }
  }
  return true;
}

function candidatos(grade, l, c) {
  const r = [];
  for (let v = 1; v <= 9; v++) if (podeColocar(grade, l, c, v)) r.push(v);
  return r;
}

function buscar(grade, limite, acumulado) {
  // MRV: escolhe a casa vazia com menos candidatos
  let melhor = null;
  for (let l = 0; l < 9; l++) {
    for (let c = 0; c < 9; c++) {
      if (grade[l][c] !== 0) continue;
      const cand = candidatos(grade, l, c);
      if (cand.length === 0) return;
      if (!melhor || cand.length < melhor.cand.length) melhor = { l, c, cand };
    }
  }
  if (!melhor) {
    acumulado.push(grade.map((x) => x.slice()));
    return;
  }
  for (const v of melhor.cand) {
    grade[melhor.l][melhor.c] = v;
    buscar(grade, limite, acumulado);
    grade[melhor.l][melhor.c] = 0;
    if (acumulado.length >= limite) return;
  }
}

/** Retorna até `limite` soluções (cópias). */
export function resolverTodas(grade, limite = 2) {
  if (!gradeConsistente(grade)) return [];
  const copia = grade.map((l) => l.slice());
  const acumulado = [];
  buscar(copia, limite, acumulado);
  return acumulado;
}

/** Primeira solução ou null. Não altera a entrada. */
export function resolver(grade) {
  return resolverTodas(grade, 1)[0] ?? null;
}

export function unica(grade) {
  return resolverTodas(grade, 2).length === 1;
}
