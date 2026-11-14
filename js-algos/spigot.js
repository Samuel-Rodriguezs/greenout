// Dígitos de pi e de e por algoritmos "spigot" (gotejamento), sem aritmética de ponto flutuante.
// Pi: spigot ilimitado de Gibbons (usa BigInt nativo). e: spigot de Sale com vetor de restos.

// Gerador infinito dos dígitos de pi: 3, 1, 4, 1, 5, ...
export function* digitosPi() {
  let q = 1n, r = 0n, t = 1n, k = 1n, n = 3n, l = 3n;
  for (;;) {
    if (4n * q + r - t < n * t) {
      yield Number(n);
      const nr = 10n * (r - n * t);
      n = (10n * (3n * q + r)) / t - 10n * n;
      q *= 10n;
      r = nr;
    } else {
      const nr = (2n * q + r) * l;
      const nn = (q * (7n * k) + 2n + r * l) / (t * l);
      q *= k;
      t *= l;
      l += 2n;
      k += 1n;
      n = nn;
      r = nr;
    }
  }
}

// String com n dígitos de pi, ex.: piString(5) = "3.1415".
export function piString(n) {
  if (!Number.isInteger(n) || n < 1) throw new RangeError('n deve ser >= 1');
  const ds = [];
  for (const d of digitosPi()) { ds.push(d); if (ds.length === n) break; }
  return n === 1 ? '3' : `${ds[0]}.${ds.slice(1).join('')}`;
}

// n casas decimais de e = 2.718281828... (n >= 0), com spigot de Sale.
export function eString(n) {
  if (!Number.isInteger(n) || n < 0) throw new RangeError('n deve ser >= 0');
  const tam = n + 10; // dígitos de guarda
  const m = tam + 20; // termos suficientes da série 1/k!
  const a = new Array(m).fill(1);
  const digitos = [];
  for (let i = 0; i < tam; i++) {
    let vai = 0;
    for (let j = m - 1; j >= 0; j--) {
      const x = 10 * a[j] + vai;
      a[j] = x % (j + 2);
      vai = Math.floor(x / (j + 2));
    }
    digitos.push(vai);
  }
  // A parte inteira (2) é implícita; digitos[i] são as casas decimais. Propaga vai-uns >= 10.
  let inteiro = 2;
  for (let i = digitos.length - 1; i >= 0; i--) {
    if (digitos[i] < 10) continue;
    const vai = Math.floor(digitos[i] / 10);
    digitos[i] %= 10;
    if (i > 0) digitos[i - 1] += vai; else inteiro += vai;
  }
  return n === 0 ? String(inteiro) : `${inteiro}.${digitos.slice(0, n).join('')}`;
}
