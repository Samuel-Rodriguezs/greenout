// Inteiros grandes não negativos como strings decimais: soma, subtração, multiplicação, fatorial.
// Implementação própria por blocos de 7 dígitos (sem usar BigInt).
const BLOCO = 7;
const BASE = 10 ** BLOCO;

function validar(s) {
  if (typeof s !== 'string' || !/^\d+$/.test(s)) throw new TypeError(`número inválido: ${s}`);
}

// string -> blocos little-endian
function paraBlocos(s) {
  validar(s);
  const b = [];
  for (let fim = s.length; fim > 0; fim -= BLOCO) b.push(Number(s.slice(Math.max(0, fim - BLOCO), fim)));
  return b;
}

function deBlocos(b) {
  let i = b.length - 1;
  while (i > 0 && b[i] === 0) i--;
  let s = String(b[i]);
  for (i--; i >= 0; i--) s += String(b[i]).padStart(BLOCO, '0');
  return s;
}

export function normalizar(s) {
  validar(s);
  return s.replace(/^0+(?=\d)/, '');
}

export function comparar(a, b) {
  a = normalizar(a); b = normalizar(b);
  if (a.length !== b.length) return a.length < b.length ? -1 : 1;
  return a < b ? -1 : a > b ? 1 : 0;
}

export function somar(a, b) {
  const x = paraBlocos(a), y = paraBlocos(b);
  const r = [];
  let vai = 0;
  for (let i = 0; i < Math.max(x.length, y.length) || vai; i++) {
    const s = (x[i] ?? 0) + (y[i] ?? 0) + vai;
    r.push(s % BASE);
    vai = s >= BASE ? 1 : 0;
  }
  return deBlocos(r);
}

// a - b, exige a >= b.
export function subtrair(a, b) {
  if (comparar(a, b) < 0) throw new RangeError('resultado negativo não suportado');
  const x = paraBlocos(a), y = paraBlocos(b);
  let empresta = 0;
  const r = x.map((d, i) => {
    let v = d - (y[i] ?? 0) - empresta;
    empresta = v < 0 ? 1 : 0;
    if (v < 0) v += BASE;
    return v;
  });
  return deBlocos(r);
}

export function multiplicar(a, b) {
  const x = paraBlocos(a), y = paraBlocos(b);
  const r = new Array(x.length + y.length).fill(0);
  for (let i = 0; i < x.length; i++) {
    let vai = 0;
    for (let j = 0; j < y.length || vai; j++) {
      // x*y < 1e14 e acumulador < 2^53: seguro
      const atual = r[i + j] + x[i] * (y[j] ?? 0) + vai;
      r[i + j] = atual % BASE;
      vai = Math.floor(atual / BASE);
    }
  }
  return deBlocos(r);
}

export function fatorial(n) {
  if (!Number.isInteger(n) || n < 0) throw new RangeError('n deve ser inteiro não negativo');
  let r = '1';
  for (let i = 2; i <= n; i++) r = multiplicar(r, String(i));
  return r;
}

export function potencia(base, exp) {
  if (!Number.isInteger(exp) || exp < 0) throw new RangeError('expoente inválido');
  let r = '1', b = normalizar(base);
  for (let e = exp; e > 0; e >>= 1) {
    if (e & 1) r = multiplicar(r, b);
    if (e > 1) b = multiplicar(b, b);
  }
  return r;
}

export function somaDigitos(s) {
  return [...normalizar(s)].reduce((t, d) => t + Number(d), 0);
}
