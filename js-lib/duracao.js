const UNIDADES = { d: 86400000, h: 3600000, m: 60000, s: 1000, ms: 1 };

// Converte "1h30m", "2d 4h", "500ms" em milissegundos.
export function parseDuracao(texto) {
  const s = String(texto).trim().toLowerCase();
  const re = /(\d+(?:\.\d+)?)\s*(ms|d|h|m|s)/g;
  let total = 0, consumido = 0, m;
  while ((m = re.exec(s)) !== null) {
    if (s.slice(consumido, m.index).trim() !== '') throw new SyntaxError(`duração inválida: "${texto}"`);
    total += parseFloat(m[1]) * UNIDADES[m[2]];
    consumido = re.lastIndex;
  }
  if (consumido === 0 || s.slice(consumido).trim() !== '') throw new SyntaxError(`duração inválida: "${texto}"`);
  return total;
}

// Inverso: 5400000 -> "1h30m".
export function formatarDuracao(ms) {
  if (ms === 0) return '0s';
  let resto = Math.abs(ms);
  let saida = '';
  for (const [u, v] of Object.entries(UNIDADES)) {
    const q = Math.floor(resto / v);
    if (q > 0) { saida += q + u; resto -= q * v; }
  }
  return (ms < 0 ? '-' : '') + saida;
}
