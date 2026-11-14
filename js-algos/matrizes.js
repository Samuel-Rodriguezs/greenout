// Álgebra linear básica: eliminação de Gauss com pivoteamento parcial.
const EPS = 1e-12;

const copiar = (m) => m.map((l) => [...l]);

function validarQuadrada(m) {
  if (!Array.isArray(m) || m.length === 0 || m.some((l) => l.length !== m.length)) {
    throw new RangeError('matriz quadrada não vazia esperada');
  }
}

export function identidade(n) {
  return Array.from({ length: n }, (_, i) => Array.from({ length: n }, (_, j) => (i === j ? 1 : 0)));
}

export function multiplicarMatrizes(a, b) {
  if (a[0].length !== b.length) throw new RangeError('dimensões incompatíveis');
  return a.map((linha) => b[0].map((_, j) => linha.reduce((s, x, k) => s + x * b[k][j], 0)));
}

export function transposta(m) {
  return m[0].map((_, j) => m.map((l) => l[j]));
}

// Determinante por Gauss (O(n^3)).
export function determinante(matriz) {
  validarQuadrada(matriz);
  const a = copiar(matriz), n = a.length;
  let det = 1;
  for (let c = 0; c < n; c++) {
    let p = c;
    for (let i = c + 1; i < n; i++) if (Math.abs(a[i][c]) > Math.abs(a[p][c])) p = i;
    if (Math.abs(a[p][c]) < EPS) return 0;
    if (p !== c) { [a[p], a[c]] = [a[c], a[p]]; det = -det; }
    det *= a[c][c];
    for (let i = c + 1; i < n; i++) {
      const f = a[i][c] / a[c][c];
      for (let j = c; j < n; j++) a[i][j] -= f * a[c][j];
    }
  }
  return det;
}

// Resolve A x = b. Lança erro se A for singular.
export function resolverSistema(A, b) {
  validarQuadrada(A);
  if (b.length !== A.length) throw new RangeError('b incompatível com A');
  const n = A.length;
  const a = A.map((l, i) => [...l, b[i]]);
  for (let c = 0; c < n; c++) {
    let p = c;
    for (let i = c + 1; i < n; i++) if (Math.abs(a[i][c]) > Math.abs(a[p][c])) p = i;
    if (Math.abs(a[p][c]) < EPS) throw new Error('matriz singular');
    [a[p], a[c]] = [a[c], a[p]];
    for (let i = c + 1; i < n; i++) {
      const f = a[i][c] / a[c][c];
      for (let j = c; j <= n; j++) a[i][j] -= f * a[c][j];
    }
  }
  const x = new Array(n).fill(0);
  for (let i = n - 1; i >= 0; i--) {
    let s = a[i][n];
    for (let j = i + 1; j < n; j++) s -= a[i][j] * x[j];
    x[i] = s / a[i][i];
  }
  return x;
}

// Inversa por Gauss-Jordan.
export function inversa(matriz) {
  validarQuadrada(matriz);
  const n = matriz.length;
  const a = matriz.map((l, i) => [...l, ...identidade(n)[i]]);
  for (let c = 0; c < n; c++) {
    let p = c;
    for (let i = c + 1; i < n; i++) if (Math.abs(a[i][c]) > Math.abs(a[p][c])) p = i;
    if (Math.abs(a[p][c]) < EPS) throw new Error('matriz singular');
    [a[p], a[c]] = [a[c], a[p]];
    const piv = a[c][c];
    for (let j = 0; j < 2 * n; j++) a[c][j] /= piv;
    for (let i = 0; i < n; i++) {
      if (i === c) continue;
      const f = a[i][c];
      for (let j = 0; j < 2 * n; j++) a[i][j] -= f * a[c][j];
    }
  }
  return a.map((l) => l.slice(n));
}

// Posto (rank) da matriz retangular.
export function posto(matriz) {
  const a = copiar(matriz);
  const linhas = a.length, cols = a[0].length;
  let r = 0;
  for (let c = 0; c < cols && r < linhas; c++) {
    let p = r;
    for (let i = r + 1; i < linhas; i++) if (Math.abs(a[i][c]) > Math.abs(a[p][c])) p = i;
    if (Math.abs(a[p][c]) < 1e-10) continue;
    [a[p], a[r]] = [a[r], a[p]];
    for (let i = r + 1; i < linhas; i++) {
      const f = a[i][c] / a[r][c];
      for (let j = c; j < cols; j++) a[i][j] -= f * a[r][j];
    }
    r++;
  }
  return r;
}
