// Valida número de cartão pelo algoritmo de Luhn (aceita espaços e hífens).
export function luhnValido(numero) {
  const s = String(numero).replace(/[\s-]/g, '');
  if (!/^\d{12,19}$/.test(s)) return false;
  return somaLuhn(s) % 10 === 0;
}

function somaLuhn(s) {
  let soma = 0;
  for (let i = 0; i < s.length; i++) {
    let d = Number(s[s.length - 1 - i]);
    if (i % 2 === 1) { d *= 2; if (d > 9) d -= 9; }
    soma += d;
  }
  return soma;
}

// Calcula o dígito verificador a anexar a um prefixo (sem o dígito final).
export function digitoLuhn(prefixo) {
  const s = String(prefixo);
  for (let d = 0; d < 10; d++) if (somaLuhn(s + d) % 10 === 0) return d;
}

// Detecta a bandeira pelo prefixo.
export function bandeira(numero) {
  const s = String(numero).replace(/\D/g, '');
  if (/^4/.test(s)) return 'visa';
  if (/^(5[1-5]|2[2-7])/.test(s)) return 'mastercard';
  if (/^3[47]/.test(s)) return 'amex';
  return 'desconhecida';
}
