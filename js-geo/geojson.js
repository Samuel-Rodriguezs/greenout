// Parser de GeoJSON (Point, LineString, Polygon) com validação.
// Aceita geometrias soltas, Feature e FeatureCollection. Posições são [lon, lat(, alt)].

export class GeoJSONError extends Error {
  constructor(mensagem, caminho = '$') {
    super(`${caminho}: ${mensagem}`);
    this.name = 'GeoJSONError';
    this.caminho = caminho;
  }
}

const TIPOS_GEOMETRIA = ['Point', 'LineString', 'Polygon'];

function posicao(pos, caminho) {
  if (!Array.isArray(pos) || pos.length < 2 || pos.length > 3) {
    throw new GeoJSONError('posição deve ter 2 ou 3 números', caminho);
  }
  if (!pos.every((v) => typeof v === 'number' && Number.isFinite(v))) {
    throw new GeoJSONError('coordenadas devem ser números finitos', caminho);
  }
  const [lon, lat] = pos;
  if (lon < -180 || lon > 180) throw new GeoJSONError(`longitude fora de [-180, 180]: ${lon}`, caminho);
  if (lat < -90 || lat > 90) throw new GeoJSONError(`latitude fora de [-90, 90]: ${lat}`, caminho);
  return [...pos];
}

function lista(v, caminho) {
  if (!Array.isArray(v)) throw new GeoJSONError('esperado array', caminho);
  return v;
}

function anel(a, caminho) {
  const pts = lista(a, caminho).map((p, i) => posicao(p, `${caminho}[${i}]`));
  if (pts.length < 4) throw new GeoJSONError('anel precisa de ao menos 4 posições', caminho);
  const p = pts[0], u = pts.at(-1);
  if (p[0] !== u[0] || p[1] !== u[1]) throw new GeoJSONError('anel não está fechado', caminho);
  return pts;
}

export function parseGeometria(g, caminho = '$') {
  if (g === null || typeof g !== 'object' || Array.isArray(g)) throw new GeoJSONError('geometria deve ser um objeto', caminho);
  const { type, coordinates } = g;
  if (!TIPOS_GEOMETRIA.includes(type)) throw new GeoJSONError(`tipo de geometria não suportado: ${String(type)}`, caminho);
  const c = `${caminho}.coordinates`;
  switch (type) {
    case 'Point':
      return { tipo: 'Point', coordenadas: posicao(coordinates, c) };
    case 'LineString': {
      const pts = lista(coordinates, c).map((p, i) => posicao(p, `${c}[${i}]`));
      if (pts.length < 2) throw new GeoJSONError('LineString precisa de ao menos 2 posições', c);
      return { tipo: 'LineString', coordenadas: pts };
    }
    default: {
      const aneis = lista(coordinates, c).map((a, i) => anel(a, `${c}[${i}]`));
      if (aneis.length === 0) throw new GeoJSONError('Polygon precisa de ao menos 1 anel', c);
      return { tipo: 'Polygon', coordenadas: aneis };
    }
  }
}

function parseFeature(f, caminho) {
  if (f === null || typeof f !== 'object' || f.type !== 'Feature') throw new GeoJSONError('esperado Feature', caminho);
  const props = f.properties ?? null;
  if (props !== null && (typeof props !== 'object' || Array.isArray(props))) {
    throw new GeoJSONError('properties deve ser objeto ou null', `${caminho}.properties`);
  }
  const geometria = f.geometry === null || f.geometry === undefined ? null : parseGeometria(f.geometry, `${caminho}.geometry`);
  return { tipo: 'Feature', id: f.id ?? null, geometria, propriedades: props };
}

/**
 * Retorna sempre uma lista de features normalizadas:
 * { tipo: 'Feature', id, geometria: {tipo, coordenadas} | null, propriedades }.
 * Geometrias soltas são embrulhadas em uma feature sem propriedades.
 */
export function parseGeoJSON(entrada) {
  let obj = entrada;
  if (typeof entrada === 'string') {
    try { obj = JSON.parse(entrada); } catch (e) { throw new GeoJSONError(`JSON inválido (${e.message})`); }
  }
  if (obj === null || typeof obj !== 'object' || Array.isArray(obj)) throw new GeoJSONError('documento deve ser um objeto');
  if (obj.type === 'FeatureCollection') {
    return lista(obj.features, '$.features').map((f, i) => parseFeature(f, `$.features[${i}]`));
  }
  if (obj.type === 'Feature') return [parseFeature(obj, '$')];
  return [{ tipo: 'Feature', id: null, geometria: parseGeometria(obj), propriedades: null }];
}
