// Geodésia em esfera: distância (haversine), rumo inicial e ponto de destino.
// Coordenadas em graus decimais: (lat, lon).

export const RAIO_TERRA_M = 6371008.8; // raio médio IUGG

const rad = (g) => (g * Math.PI) / 180;
const grau = (r) => (r * 180) / Math.PI;

export function normalizaLon(lon) {
  return ((((lon + 180) % 360) + 360) % 360) - 180;
}

function valida(lat, lon) {
  if (!Number.isFinite(lat) || !Number.isFinite(lon) || Math.abs(lat) > 90) {
    throw new RangeError(`coordenada inválida: ${lat}, ${lon}`);
  }
}

/** Distância em metros pelo círculo máximo. */
export function distanciaHaversine(lat1, lon1, lat2, lon2, raio = RAIO_TERRA_M) {
  valida(lat1, lon1);
  valida(lat2, lon2);
  const dLat = rad(lat2 - lat1);
  const dLon = rad(lon2 - lon1);
  const h = Math.sin(dLat / 2) ** 2 + Math.cos(rad(lat1)) * Math.cos(rad(lat2)) * Math.sin(dLon / 2) ** 2;
  return 2 * raio * Math.asin(Math.min(1, Math.sqrt(h)));
}

/** Rumo inicial (azimute) em graus, 0 = norte, no intervalo [0, 360). */
export function rumoInicial(lat1, lon1, lat2, lon2) {
  valida(lat1, lon1);
  valida(lat2, lon2);
  const f1 = rad(lat1), f2 = rad(lat2), dl = rad(lon2 - lon1);
  const y = Math.sin(dl) * Math.cos(f2);
  const x = Math.cos(f1) * Math.sin(f2) - Math.sin(f1) * Math.cos(f2) * Math.cos(dl);
  return (grau(Math.atan2(y, x)) + 360) % 360;
}

/** Ponto alcançado ao andar `dist` metros a partir de (lat, lon) com rumo `rumo`. */
export function destino(lat, lon, rumo, dist, raio = RAIO_TERRA_M) {
  valida(lat, lon);
  const d = dist / raio;
  const b = rad(rumo);
  const f1 = rad(lat), l1 = rad(lon);
  const f2 = Math.asin(Math.sin(f1) * Math.cos(d) + Math.cos(f1) * Math.sin(d) * Math.cos(b));
  const l2 = l1 + Math.atan2(Math.sin(b) * Math.sin(d) * Math.cos(f1), Math.cos(d) - Math.sin(f1) * Math.sin(f2));
  return [grau(f2), normalizaLon(grau(l2))];
}

/** Ponto médio do arco entre dois pontos. */
export function pontoMedio(lat1, lon1, lat2, lon2) {
  const f1 = rad(lat1), l1 = rad(lon1), f2 = rad(lat2), dl = rad(lon2 - lon1);
  const bx = Math.cos(f2) * Math.cos(dl);
  const by = Math.cos(f2) * Math.sin(dl);
  const fm = Math.atan2(Math.sin(f1) + Math.sin(f2), Math.hypot(Math.cos(f1) + bx, by));
  const lm = l1 + Math.atan2(by, Math.cos(f1) + bx);
  return [grau(fm), normalizaLon(grau(lm))];
}
