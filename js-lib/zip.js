// Combina arrays posição a posição (usa o menor comprimento).
export function zip(...listas) {
  if (listas.length === 0) return [];
  const n = Math.min(...listas.map((l) => l.length));
  return Array.from({ length: n }, (_, i) => listas.map((l) => l[i]));
}
// Operação inversa de zip.
export function unzip(pares) {
  if (pares.length === 0) return [];
  const n = Math.min(...pares.map((p) => p.length));
  return Array.from({ length: n }, (_, i) => pares.map((p) => p[i]));
}
