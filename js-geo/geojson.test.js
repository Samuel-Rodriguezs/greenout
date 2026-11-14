import test from 'node:test';
import assert from 'node:assert/strict';
import { parseGeoJSON, parseGeometria, GeoJSONError } from './geojson.js';

test('Point solto (São Paulo, lon antes de lat)', () => {
  const [f] = parseGeoJSON({ type: 'Point', coordinates: [-46.6333, -23.5505] });
  assert.deepEqual(f.geometria, { tipo: 'Point', coordenadas: [-46.6333, -23.5505] });
  assert.equal(f.propriedades, null);
});

test('Feature com propriedades e altitude', () => {
  const [f] = parseGeoJSON(JSON.stringify({
    type: 'Feature', id: 7,
    properties: { nome: 'Cristo Redentor' },
    geometry: { type: 'Point', coordinates: [-43.2105, -22.9519, 710] },
  }));
  assert.equal(f.id, 7);
  assert.equal(f.propriedades.nome, 'Cristo Redentor');
  assert.equal(f.geometria.coordenadas.length, 3);
});

test('LineString válida', () => {
  const g = parseGeometria({ type: 'LineString', coordinates: [[-46.63, -23.55], [-43.17, -22.90]] });
  assert.equal(g.coordenadas.length, 2);
});

test('Polygon com anel externo e buraco', () => {
  const ext = [[0, 0], [10, 0], [10, 10], [0, 10], [0, 0]];
  const furo = [[2, 2], [4, 2], [4, 4], [2, 4], [2, 2]];
  const g = parseGeometria({ type: 'Polygon', coordinates: [ext, furo] });
  assert.equal(g.coordenadas.length, 2);
});

test('FeatureCollection com várias geometrias e geometry null', () => {
  const fs = parseGeoJSON({
    type: 'FeatureCollection',
    features: [
      { type: 'Feature', properties: {}, geometry: { type: 'Point', coordinates: [1, 2] } },
      { type: 'Feature', properties: null, geometry: null },
    ],
  });
  assert.equal(fs.length, 2);
  assert.equal(fs[1].geometria, null);
});

test('resultado é cópia: alterar a saída não altera a entrada', () => {
  const entrada = { type: 'Point', coordinates: [1, 2] };
  const [f] = parseGeoJSON(entrada);
  f.geometria.coordenadas[0] = 99;
  assert.equal(entrada.coordinates[0], 1);
});

test('longitude e latitude fora do intervalo', () => {
  assert.throws(() => parseGeometria({ type: 'Point', coordinates: [181, 0] }), /longitude/);
  assert.throws(() => parseGeometria({ type: 'Point', coordinates: [0, -91] }), /latitude/);
  assert.ok(parseGeometria({ type: 'Point', coordinates: [180, 90] }));
});

test('posição malformada', () => {
  assert.throws(() => parseGeometria({ type: 'Point', coordinates: [1] }), GeoJSONError);
  assert.throws(() => parseGeometria({ type: 'Point', coordinates: [1, 2, 3, 4] }), GeoJSONError);
  assert.throws(() => parseGeometria({ type: 'Point', coordinates: ['1', 2] }), /finitos/);
  assert.throws(() => parseGeometria({ type: 'Point', coordinates: [NaN, 2] }), /finitos/);
});

test('LineString com uma posição é rejeitada', () => {
  assert.throws(() => parseGeometria({ type: 'LineString', coordinates: [[0, 0]] }), /ao menos 2/);
});

test('Polygon: anel aberto ou curto é rejeitado', () => {
  assert.throws(() => parseGeometria({ type: 'Polygon', coordinates: [[[0, 0], [1, 0], [1, 1], [0, 1]]] }), /fechado/);
  assert.throws(() => parseGeometria({ type: 'Polygon', coordinates: [[[0, 0], [1, 0], [0, 0]]] }), /4 posições/);
  assert.throws(() => parseGeometria({ type: 'Polygon', coordinates: [] }), /ao menos 1 anel/);
});

test('mensagem de erro inclui o caminho do problema', () => {
  const doc = { type: 'FeatureCollection', features: [{ type: 'Feature', properties: {}, geometry: { type: 'Point', coordinates: [0, 95] } }] };
  assert.throws(() => parseGeoJSON(doc), (e) => e.caminho === '$.features[0].geometry.coordinates' && /latitude/.test(e.message));
});

test('tipos não suportados, JSON inválido e documentos errados', () => {
  assert.throws(() => parseGeometria({ type: 'MultiPoint', coordinates: [] }), /não suportado/);
  assert.throws(() => parseGeoJSON('{nao é json'), /JSON inválido/);
  assert.throws(() => parseGeoJSON(null), GeoJSONError);
  assert.throws(() => parseGeoJSON([]), GeoJSONError);
  assert.throws(() => parseGeoJSON({ type: 'FeatureCollection' }), /array/);
  assert.throws(() => parseGeoJSON({ type: 'Feature', properties: 5, geometry: null }), /properties/);
});
