// Geohash: codificação base32 por bisseção alternada de longitude e latitude.

const BASE32 = '0123456789bcdefghjkmnpqrstuvwxyz';
const INDICE = new Map([...BASE32].map((c, i) => [c, i]));

export function codifica(lat, lon, precisao = 9) {
  if (!Number.isInteger(precisao) || precisao < 1 || precisao > 12) throw new RangeError('precisão deve ser 1..12');
  if (!(Math.abs(lat) <= 90) || !(Math.abs(lon) <= 180)) throw new RangeError('coordenada fora do intervalo');
  let latMin = -90, latMax = 90, lonMin = -180, lonMax = 180;
  let par = true, bits = 0, valor = 0, hash = '';
  while (hash.length < precisao) {
    if (par) {
      const meio = (lonMin + lonMax) / 2;
      if (lon >= meio) { valor = valor * 2 + 1; lonMin = meio; } else { valor *= 2; lonMax = meio; }
    } else {
      const meio = (latMin + latMax) / 2;
      if (lat >= meio) { valor = valor * 2 + 1; latMin = meio; } else { valor *= 2; latMax = meio; }
    }
    par = !par;
    if (++bits === 5) {
      hash += BASE32[valor];
      bits = 0;
      valor = 0;
    }
  }
  return hash;
}

/** Caixa da célula: { latMin, latMax, lonMin, lonMax }. */
export function decodificaBBox(hash) {
  if (typeof hash !== 'string' || hash.length === 0) throw new TypeError('geohash vazio');
  let latMin = -90, latMax = 90, lonMin = -180, lonMax = 180;
  let par = true;
  for (const c of hash.toLowerCase()) {
    const v = INDICE.get(c);
    if (v === undefined) throw new RangeError(`caractere inválido em geohash: ${c}`);
    for (let b = 4; b >= 0; b--) {
      const bit = (v >> b) & 1;
      if (par) {
        const meio = (lonMin + lonMax) / 2;
        if (bit) lonMin = meio; else lonMax = meio;
      } else {
        const meio = (latMin + latMax) / 2;
        if (bit) latMin = meio; else latMax = meio;
      }
      par = !par;
    }
  }
  return { latMin, latMax, lonMin, lonMax };
}

/** Centro da célula como [lat, lon]. */
export function decodifica(hash) {
  const b = decodificaBBox(hash);
  return [(b.latMin + b.latMax) / 2, (b.lonMin + b.lonMax) / 2];
}

const DIRECOES = {
  n: [1, 0], s: [-1, 0], e: [0, 1], w: [0, -1],
  ne: [1, 1], nw: [1, -1], se: [-1, 1], sw: [-1, -1],
};

/** Vizinho na direção dada, ou null além dos polos. A longitude dá a volta. */
export function vizinho(hash, direcao) {
  const d = DIRECOES[direcao];
  if (!d) throw new RangeError(`direção inválida: ${direcao}`);
  const b = decodificaBBox(hash);
  const [lat, lon] = [(b.latMin + b.latMax) / 2, (b.lonMin + b.lonMax) / 2];
  const novaLat = lat + d[0] * (b.latMax - b.latMin);
  if (novaLat > 90 || novaLat < -90) return null;
  let novaLon = lon + d[1] * (b.lonMax - b.lonMin);
  if (novaLon > 180) novaLon -= 360;
  if (novaLon < -180) novaLon += 360;
  return codifica(novaLat, novaLon, hash.length);
}

/** Os até 8 vizinhos, indexados pela direção (null nos polos). */
export function vizinhos(hash) {
  return Object.fromEntries(Object.keys(DIRECOES).map((d) => [d, vizinho(hash, d)]));
}
