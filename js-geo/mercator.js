// Projeção Web Mercator (EPSG:3857) e esquema de tiles XYZ (slippy map).

export const RAIO_MERCATOR = 6378137;
export const LAT_MAX = 85.0511287798066;
const METADE = Math.PI * RAIO_MERCATOR; // 20037508.342789244

const rad = (g) => (g * Math.PI) / 180;
const grau = (r) => (r * 180) / Math.PI;

/** (lat, lon) em graus -> [x, y] em metros. */
export function latLonParaMetros(lat, lon) {
  if (Math.abs(lat) > LAT_MAX) throw new RangeError(`latitude fora do domínio Web Mercator: ${lat}`);
  const x = RAIO_MERCATOR * rad(lon);
  const y = RAIO_MERCATOR * Math.log(Math.tan(Math.PI / 4 + rad(lat) / 2));
  return [x, y];
}

/** [x, y] em metros -> [lat, lon] em graus. */
export function metrosParaLatLon(x, y) {
  const lon = grau(x / RAIO_MERCATOR);
  const lat = grau(2 * Math.atan(Math.exp(y / RAIO_MERCATOR)) - Math.PI / 2);
  return [lat, lon];
}

/** Tile XYZ que contém o ponto no zoom dado. */
export function latLonParaTile(lat, lon, zoom) {
  if (!Number.isInteger(zoom) || zoom < 0 || zoom > 30) throw new RangeError('zoom inválido');
  if (Math.abs(lat) > LAT_MAX) throw new RangeError('latitude fora do domínio Web Mercator');
  const n = 2 ** zoom;
  const latR = rad(lat);
  let x = Math.floor(((lon + 180) / 360) * n);
  let y = Math.floor(((1 - Math.log(Math.tan(latR) + 1 / Math.cos(latR)) / Math.PI) / 2) * n);
  x = Math.min(Math.max(x, 0), n - 1); // lon = 180 cai no último tile
  y = Math.min(Math.max(y, 0), n - 1);
  return { z: zoom, x, y };
}

/** Canto noroeste do tile, em [lat, lon]. */
export function tileParaLatLon(z, x, y) {
  const n = 2 ** z;
  if (x < 0 || y < 0 || x > n || y > n) throw new RangeError('tile fora do intervalo');
  const lon = (x / n) * 360 - 180;
  const lat = grau(Math.atan(Math.sinh(Math.PI * (1 - (2 * y) / n))));
  return [lat, lon];
}

/** Limites do tile: { norte, sul, oeste, leste } em graus. */
export function limitesDoTile(z, x, y) {
  const [norte, oeste] = tileParaLatLon(z, x, y);
  const [sul, leste] = tileParaLatLon(z, x + 1, y + 1);
  return { norte, sul, oeste, leste };
}

/** Quadkey (Bing) do tile. */
export function tileParaQuadkey(z, x, y) {
  let q = '';
  for (let i = z; i > 0; i--) {
    const m = 1 << (i - 1);
    q += ((x & m ? 1 : 0) + (y & m ? 2 : 0)).toString();
  }
  return q;
}

/** Metros por pixel no equador para tiles de 256px. */
export function resolucao(zoom) {
  return (2 * METADE) / (256 * 2 ** zoom);
}
