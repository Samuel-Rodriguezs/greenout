export const ehEmail = (s) =>
  typeof s === 'string' && s.length <= 254 && /^[A-Za-z0-9._%+-]+@[A-Za-z0-9-]+(\.[A-Za-z0-9-]+)*\.[A-Za-z]{2,}$/.test(s);

export function ehURL(s, protocolos = ['http:', 'https:']) {
  try { return protocolos.includes(new URL(s).protocol); } catch { return false; }
}

const soDigitos = (s) => String(s).replace(/\D/g, '');

export function ehCPF(valor) {
  const c = soDigitos(valor);
  if (c.length !== 11 || /^(\d)\1{10}$/.test(c)) return false;
  for (const t of [9, 10]) {
    let soma = 0;
    for (let i = 0; i < t; i++) soma += Number(c[i]) * (t + 1 - i);
    const dv = ((soma * 10) % 11) % 10;
    if (dv !== Number(c[t])) return false;
  }
  return true;
}

export function ehCNPJ(valor) {
  const c = soDigitos(valor);
  if (c.length !== 14 || /^(\d)\1{13}$/.test(c)) return false;
  for (const t of [12, 13]) {
    const pesos = t === 12 ? [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2] : [6, 5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2];
    const soma = pesos.reduce((s, p, i) => s + p * Number(c[i]), 0);
    const r = soma % 11;
    if ((r < 2 ? 0 : 11 - r) !== Number(c[t])) return false;
  }
  return true;
}
