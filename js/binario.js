// Conversão entre decimal e binário implementada à mão (sem toString(2) / parseInt).

/** Inteiro (inclusive negativo) para string binária, ex.: 10 -> "1010", -5 -> "-101". */
export function decimalParaBinario(n) {
  if (!Number.isSafeInteger(n)) throw new RangeError('n deve ser um inteiro seguro');
  if (n === 0) return '0';
  const negativo = n < 0;
  let resto = Math.abs(n);
  const bits = [];
  while (resto > 0) {
    bits.push(resto % 2);
    resto = Math.floor(resto / 2);
  }
  return (negativo ? '-' : '') + bits.reverse().join('');
}

/** String binária (com sinal opcional) para inteiro. */
export function binarioParaDecimal(texto) {
  if (typeof texto !== 'string' || !/^-?[01]+$/.test(texto)) {
    throw new SyntaxError(`binário inválido: ${texto}`);
  }
  const negativo = texto[0] === '-';
  const bits = negativo ? texto.slice(1) : texto;
  let total = 0;
  for (const bit of bits) total = total * 2 + (bit === '1' ? 1 : 0);
  if (!Number.isSafeInteger(total)) throw new RangeError('valor fora do intervalo seguro');
  return negativo ? -total : total;
}
