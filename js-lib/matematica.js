export const clamp = (v, min, max) => {
  if (min > max) throw new RangeError('min não pode ser maior que max');
  return Math.min(max, Math.max(min, v));
};
// Interpolação linear entre a e b, t em [0,1].
export const lerp = (a, b, t) => a + (b - a) * t;
// Inverso de lerp: onde v está entre a e b.
export const inverseLerp = (a, b, v) => (a === b ? 0 : (v - a) / (b - a));
// Converte v do intervalo [a1,b1] para [a2,b2].
export const remap = (v, a1, b1, a2, b2) => lerp(a2, b2, inverseLerp(a1, b1, v));
