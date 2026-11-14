// Crivo de Eratóstenes simples e segmentado (memória O(sqrt(n) + tamanho do segmento)).

// Primos até n (inclusive) com crivo simples.
export function crivo(n) {
  if (n < 2) return [];
  const composto = new Uint8Array(n + 1);
  const primos = [];
  for (let i = 2; i <= n; i++) {
    if (composto[i]) continue;
    primos.push(i);
    for (let j = i * i; j <= n; j += i) composto[j] = 1;
  }
  return primos;
}

// Primos em [lo, hi] (inclusive) processando em segmentos.
export function crivoSegmentado(lo, hi, tamSegmento = 32768) {
  if (!Number.isInteger(lo) || !Number.isInteger(hi)) throw new TypeError('limites devem ser inteiros');
  if (hi < lo) return [];
  lo = Math.max(lo, 2);
  if (hi < lo) return [];
  const base = crivo(Math.floor(Math.sqrt(hi)));
  const resultado = [];
  for (let ini = lo; ini <= hi; ini += tamSegmento) {
    const fim = Math.min(ini + tamSegmento - 1, hi);
    const marca = new Uint8Array(fim - ini + 1);
    for (const p of base) {
      if (p * p > fim) break;
      for (let m = Math.max(p * p, Math.ceil(ini / p) * p); m <= fim; m += p) marca[m - ini] = 1;
    }
    for (let i = 0; i < marca.length; i++) if (!marca[i]) resultado.push(ini + i);
  }
  return resultado;
}

// Quantidade de primos <= n.
export const contarPrimos = (n) => crivoSegmentado(2, n).length;

// Teste de primalidade determinístico para n < 2^53 por divisão com 6k±1.
export function ehPrimo(n) {
  if (!Number.isInteger(n) || n < 2) return false;
  if (n < 4) return true;
  if (n % 2 === 0 || n % 3 === 0) return false;
  for (let i = 5; i * i <= n; i += 6) if (n % i === 0 || n % (i + 2) === 0) return false;
  return true;
}

// Fatoração em primos: { primo: expoente }.
export function fatorar(n) {
  if (!Number.isInteger(n) || n < 2) throw new RangeError('n deve ser inteiro >= 2');
  const f = {};
  for (let p = 2; p * p <= n; p += p === 2 ? 1 : 2) {
    while (n % p === 0) { f[p] = (f[p] ?? 0) + 1; n /= p; }
  }
  if (n > 1) f[n] = (f[n] ?? 0) + 1;
  return f;
}
