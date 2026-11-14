// Área aproximada de polígono sobre a esfera (graus lat/lon -> m²).
// Usa a integral de Chamberlain-Duquette: boa para polígonos pequenos/médios
// cujas arestas se aproximam de linhas lat/lon (erro cresce com arestas longas).
import { RAIO_TERRA_M } from './haversine.js';

const rad = (g) => (g * Math.PI) / 180;

/** Anel como [[lat, lon], ...]. Retorna a área positiva em m². */
export function areaEsferica(anel, raio = RAIO_TERRA_M) {
  let pts = anel;
  const n0 = pts.length;
  if (n0 > 1 && pts[0][0] === pts[n0 - 1][0] && pts[0][1] === pts[n0 - 1][1]) pts = pts.slice(0, -1);
  if (pts.length < 3) throw new RangeError('polígono precisa de ao menos 3 vértices');
  let soma = 0;
  for (let i = 0; i < pts.length; i++) {
    const [lat1, lon1] = pts[i];
    const [lat2, lon2] = pts[(i + 1) % pts.length];
    if (Math.abs(lat1) > 90 || Math.abs(lat2) > 90) throw new RangeError('latitude fora de [-90, 90]');
    let dLon = lon2 - lon1;
    if (dLon > 180) dLon -= 360; // atravessa o antimeridiano pelo lado curto
    else if (dLon < -180) dLon += 360;
    soma += rad(dLon) * (2 + Math.sin(rad(lat1)) + Math.sin(rad(lat2)));
  }
  return Math.abs((soma * raio * raio) / 2);
}

/** Área exata de uma "caixa" lat/lon: R² * Δλ * (sin φ2 - sin φ1). */
export function areaCaixaLatLon(latSul, latNorte, lonOeste, lonLeste, raio = RAIO_TERRA_M) {
  if (latSul > latNorte) throw new RangeError('latSul > latNorte');
  let dLon = lonLeste - lonOeste;
  if (dLon < 0) dLon += 360;
  return raio * raio * rad(dLon) * (Math.sin(rad(latNorte)) - Math.sin(rad(latSul)));
}

/** Área de GeoJSON Polygon (posições [lon, lat]): anel externo menos buracos. */
export function areaPoligonoGeoJSON(aneis, raio = RAIO_TERRA_M) {
  const [externo, ...buracos] = aneis.map((a) => a.map(([lon, lat]) => [lat, lon]));
  return areaEsferica(externo, raio) - buracos.reduce((s, b) => s + areaEsferica(b, raio), 0);
}
