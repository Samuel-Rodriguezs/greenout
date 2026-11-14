// Validação, geração de dígitos e formatação de CPF.

function calcularDigito(digitos) {
  const peso = digitos.length + 1;
  const soma = digitos.reduce((acc, d, i) => acc + d * (peso - i), 0);
  const resto = (soma * 10) % 11;
  return resto === 10 ? 0 : resto;
}

/** Remove máscara; retorna só os dígitos. */
export function limparCpf(cpf) {
  return String(cpf ?? '').replace(/\D/g, '');
}

export function validarCpf(cpf) {
  if (typeof cpf !== 'string') return false;
  // Aceita apenas dígitos puros ou a máscara 000.000.000-00.
  if (!/^(\d{11}|\d{3}\.\d{3}\.\d{3}-\d{2})$/.test(cpf)) return false;
  const numeros = limparCpf(cpf).split('').map(Number);
  if (numeros.every((n) => n === numeros[0])) return false; // 111.111.111-11 etc.
  const d1 = calcularDigito(numeros.slice(0, 9));
  const d2 = calcularDigito(numeros.slice(0, 10).map((n, i) => (i === 9 ? d1 : n)));
  return d1 === numeros[9] && d2 === numeros[10];
}

export function formatarCpf(cpf) {
  const d = limparCpf(cpf);
  if (d.length !== 11) throw new RangeError('CPF deve ter 11 dígitos');
  return `${d.slice(0, 3)}.${d.slice(3, 6)}.${d.slice(6, 9)}-${d.slice(9)}`;
}

/** Completa uma base de 9 dígitos com os dois dígitos verificadores. */
export function completarCpf(base) {
  const nove = limparCpf(base);
  if (nove.length !== 9) throw new RangeError('a base deve ter 9 dígitos');
  const numeros = nove.split('').map(Number);
  const d1 = calcularDigito(numeros);
  const d2 = calcularDigito([...numeros, d1]);
  return `${nove}${d1}${d2}`;
}
