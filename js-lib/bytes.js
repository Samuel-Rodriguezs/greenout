// Formata bytes em unidade legível. base 1024 (KiB...) por padrão ou 1000 (kB...).
export function formatarBytes(n, { casas = 2, base = 1024 } = {}) {
  if (!Number.isFinite(n) || n < 0) throw new RangeError('n deve ser número >= 0');
  const un = base === 1024 ? ['B', 'KiB', 'MiB', 'GiB', 'TiB', 'PiB'] : ['B', 'kB', 'MB', 'GB', 'TB', 'PB'];
  let i = 0;
  while (n >= base && i < un.length - 1) { n /= base; i++; }
  return `${i === 0 ? n : Number(n.toFixed(casas))} ${un[i]}`;
}
// Converte "1.5 MiB" / "2kB" de volta para bytes.
export function parseBytes(texto) {
  const m = /^\s*(\d+(?:\.\d+)?)\s*(b|kib|mib|gib|tib|kb|mb|gb|tb)?\s*$/i.exec(texto);
  if (!m) throw new SyntaxError(`tamanho inválido: "${texto}"`);
  const mult = { b: 1, kib: 1024, mib: 1024 ** 2, gib: 1024 ** 3, tib: 1024 ** 4, kb: 1e3, mb: 1e6, gb: 1e9, tb: 1e12 };
  return Math.round(parseFloat(m[1]) * mult[(m[2] ?? 'b').toLowerCase()]);
}
