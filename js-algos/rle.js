// Run-length encoding. Formato textual: <quantidade><caractere>, ex.: "3a2b1c".
// Dígitos no texto original são escapados com '\' para não ambiguar a quantidade.
export function rleCodificar(texto) {
  let saida = '';
  const chars = [...texto];
  for (let i = 0; i < chars.length;) {
    let j = i;
    while (j < chars.length && chars[j] === chars[i]) j++;
    const c = chars[i];
    saida += (j - i) + (/[0-9\\]/.test(c) ? '\\' + c : c);
    i = j;
  }
  return saida;
}

export function rleDecodificar(codigo) {
  let saida = '';
  const chars = [...codigo];
  for (let i = 0; i < chars.length;) {
    let n = '';
    while (i < chars.length && /[0-9]/.test(chars[i])) n += chars[i++];
    if (n === '' || i >= chars.length) throw new SyntaxError('RLE malformado');
    let c = chars[i++];
    if (c === '\\') {
      if (i >= chars.length) throw new SyntaxError('escape sem caractere');
      c = chars[i++];
    }
    saida += c.repeat(Number(n));
  }
  return saida;
}

// Variante binária: bytes -> pares [valor, repetições] (repetições até 255).
export function rleBytes(bytes) {
  const pares = [];
  for (const b of bytes) {
    const ult = pares[pares.length - 1];
    if (ult && ult[0] === b && ult[1] < 255) ult[1]++;
    else pares.push([b, 1]);
  }
  return pares;
}

export function rleBytesDecodificar(pares) {
  return pares.flatMap(([b, n]) => new Array(n).fill(b));
}
