// Gerador pseudoaleatório determinístico mulberry32; retorna função que dá floats em [0,1).
export function mulberry32(seed) {
  let a = seed >>> 0;
  return () => {
    a = (a + 0x6d2b79f5) >>> 0;
    let t = a;
    t = Math.imul(t ^ (t >>> 15), t | 1);
    t ^= t + Math.imul(t ^ (t >>> 7), t | 61);
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}
// Inteiro em [min, max] usando o gerador dado.
export const inteiroEntre = (rng, min, max) => min + Math.floor(rng() * (max - min + 1));
// Embaralha (Fisher-Yates) sem mutar.
export function embaralhar(lista, rng = Math.random) {
  const c = [...lista];
  for (let i = c.length - 1; i > 0; i--) {
    const j = Math.floor(rng() * (i + 1));
    [c[i], c[j]] = [c[j], c[i]];
  }
  return c;
}
