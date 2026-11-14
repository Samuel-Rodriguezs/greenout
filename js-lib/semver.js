const RE = /^v?(\d+)\.(\d+)\.(\d+)(?:-([0-9A-Za-z.-]+))?(?:\+[0-9A-Za-z.-]+)?$/;

export function parseSemver(v) {
  const m = RE.exec(String(v).trim());
  if (!m) throw new TypeError(`versão inválida: ${v}`);
  return { major: +m[1], minor: +m[2], patch: +m[3], pre: m[4] ? m[4].split('.') : [] };
}

function compararPre(a, b) {
  if (a.length === 0 && b.length === 0) return 0;
  if (a.length === 0) return 1; // sem pre-release é maior
  if (b.length === 0) return -1;
  for (let i = 0; i < Math.max(a.length, b.length); i++) {
    if (a[i] === undefined) return -1;
    if (b[i] === undefined) return 1;
    const na = /^\d+$/.test(a[i]), nb = /^\d+$/.test(b[i]);
    if (na && nb) { if (+a[i] !== +b[i]) return +a[i] < +b[i] ? -1 : 1; }
    else if (na) return -1;
    else if (nb) return 1;
    else if (a[i] !== b[i]) return a[i] < b[i] ? -1 : 1;
  }
  return 0;
}

// Retorna -1, 0 ou 1 (metadados de build "+x" são ignorados).
export function compararSemver(a, b) {
  const x = parseSemver(a), y = parseSemver(b);
  for (const k of ['major', 'minor', 'patch']) if (x[k] !== y[k]) return x[k] < y[k] ? -1 : 1;
  return compararPre(x.pre, y.pre);
}
export const ordenarVersoes = (lista) => [...lista].sort(compararSemver);
