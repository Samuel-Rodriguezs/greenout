// FizzBuzz em estilo funcional: sem laços imperativos, apenas Array.from e map.

/** Converte um número na sua palavra FizzBuzz. */
export function fizzbuzzDe(n) {
  if (n % 15 === 0) return 'FizzBuzz';
  if (n % 3 === 0) return 'Fizz';
  if (n % 5 === 0) return 'Buzz';
  return String(n);
}

/** Retorna a sequência de 1 até `limite` (inclusive). */
export function fizzbuzz(limite) {
  if (!Number.isInteger(limite) || limite < 0) {
    throw new RangeError('limite deve ser um inteiro não negativo');
  }
  return Array.from({ length: limite }, (_, i) => fizzbuzzDe(i + 1));
}
