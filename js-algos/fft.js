// FFT radix-2 (Cooley-Tukey) com números complexos próprios.
export class Complexo {
  constructor(re = 0, im = 0) { this.re = re; this.im = im; }
  somar(o) { return new Complexo(this.re + o.re, this.im + o.im); }
  subtrair(o) { return new Complexo(this.re - o.re, this.im - o.im); }
  multiplicar(o) { return new Complexo(this.re * o.re - this.im * o.im, this.re * o.im + this.im * o.re); }
  conjugado() { return new Complexo(this.re, -this.im); }
  escalar(k) { return new Complexo(this.re * k, this.im * k); }
  get modulo() { return Math.hypot(this.re, this.im); }
  get fase() { return Math.atan2(this.im, this.re); }
  static polar(r, theta) { return new Complexo(r * Math.cos(theta), r * Math.sin(theta)); }
}

const ehPotenciaDe2 = (n) => n > 0 && (n & (n - 1)) === 0;

// Transformada de Fourier (vetor de Complexo ou números; tamanho potência de 2).
export function fft(entrada, inverso = false) {
  const n = entrada.length;
  if (!ehPotenciaDe2(n)) throw new RangeError('tamanho deve ser potência de 2');
  const a = entrada.map((x) => (x instanceof Complexo ? x : new Complexo(x, 0)));
  // permutação bit-reversal
  for (let i = 1, j = 0; i < n; i++) {
    let bit = n >> 1;
    for (; j & bit; bit >>= 1) j ^= bit;
    j ^= bit;
    if (i < j) [a[i], a[j]] = [a[j], a[i]];
  }
  for (let len = 2; len <= n; len <<= 1) {
    const ang = ((inverso ? 2 : -2) * Math.PI) / len;
    for (let i = 0; i < n; i += len) {
      for (let k = 0; k < len / 2; k++) {
        const w = Complexo.polar(1, ang * k);
        const u = a[i + k], v = a[i + k + len / 2].multiplicar(w);
        a[i + k] = u.somar(v);
        a[i + k + len / 2] = u.subtrair(v);
      }
    }
  }
  return inverso ? a.map((x) => x.escalar(1 / n)) : a;
}

export const ifft = (x) => fft(x, true);

// Multiplicação de polinômios (coeficientes reais, menor grau primeiro) via FFT.
export function multiplicarPolinomios(p, q) {
  if (p.length === 0 || q.length === 0) return [];
  const tamanho = p.length + q.length - 1;
  let n = 1;
  while (n < tamanho) n <<= 1;
  const pad = (v) => [...v, ...new Array(n - v.length).fill(0)];
  const fp = fft(pad(p)), fq = fft(pad(q));
  const prod = ifft(fp.map((x, i) => x.multiplicar(fq[i])));
  return prod.slice(0, tamanho).map((c) => Math.round(c.re * 1e9) / 1e9 + 0); // "+ 0" evita -0
}

// Magnitudes do espectro de um sinal real.
export function espectro(sinal) {
  return fft(sinal).map((c) => c.modulo);
}
