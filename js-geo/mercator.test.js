import test from 'node:test';
import assert from 'node:assert/strict';
import {
  latLonParaMetros, metrosParaLatLon, latLonParaTile, tileParaLatLon, limitesDoTile,
  tileParaQuadkey, resolucao, LAT_MAX,
} from './mercator.js';

const perto = (a, b, eps) => assert.ok(Math.abs(a - b) <= eps, `${a} != ${b}`);

test('origem e extremos da projeção', () => {
  const [x0, y0] = latLonParaMetros(0, 0);
  assert.equal(x0, 0);
  perto(y0, 0, 1e-8);
  perto(latLonParaMetros(0, 180)[0], 20037508.342789244, 1e-6);
  perto(latLonParaMetros(LAT_MAX, 0)[1], 20037508.34, 0.01);
});

test('Londres projetada (valor conhecido em EPSG:3857)', () => {
  const [x, y] = latLonParaMetros(51.5074, -0.1278);
  perto(x, -14226.63, 0.01);
  perto(y, 6711542.48, 0.01);
});

test('ida e volta lat/lon <-> metros', () => {
  for (const [lat, lon] of [[-23.5505, -46.6333], [48.8566, 2.3522], [-77.85, 166.67]]) {
    const [la, lo] = metrosParaLatLon(...latLonParaMetros(lat, lon));
    perto(la, lat, 1e-9);
    perto(lo, lon, 1e-9);
  }
});

test('latitude polar lança erro', () => {
  assert.throws(() => latLonParaMetros(89, 0), RangeError);
  assert.throws(() => latLonParaTile(-90, 0, 3), RangeError);
});

test('tile de Londres no zoom 10 é 511/340', () => {
  assert.deepEqual(latLonParaTile(51.5074, -0.1278, 10), { z: 10, x: 511, y: 340 });
});

test('tile de São Paulo no zoom 10 e no zoom 0', () => {
  assert.deepEqual(latLonParaTile(-23.5505, -46.6333, 10), { z: 10, x: 379, y: 580 });
  assert.deepEqual(latLonParaTile(-23.5505, -46.6333, 0), { z: 0, x: 0, y: 0 });
});

test('lon = 180 cai no último tile', () => {
  assert.equal(latLonParaTile(0, 180, 2).x, 3);
});

test('tile -> canto noroeste e contém o ponto original', () => {
  const t = latLonParaTile(35.6762, 139.6503, 12); // Tóquio
  const l = limitesDoTile(t.z, t.x, t.y);
  assert.ok(35.6762 <= l.norte && 35.6762 >= l.sul);
  assert.ok(139.6503 >= l.oeste && 139.6503 <= l.leste);
  assert.deepEqual(tileParaLatLon(0, 0, 0).map((v) => Math.round(v * 1e4) / 1e4), [LAT_MAX, -180].map((v) => Math.round(v * 1e4) / 1e4));
});

test('quadkey do exemplo da documentação Bing', () => {
  assert.equal(tileParaQuadkey(3, 3, 5), '213');
  assert.equal(tileParaQuadkey(0, 0, 0), '');
});

test('resolução cai pela metade a cada zoom', () => {
  perto(resolucao(0), 156543.03392804097, 1e-6);
  perto(resolucao(1), resolucao(0) / 2, 1e-9);
});

test('zoom inválido lança erro', () => {
  assert.throws(() => latLonParaTile(0, 0, -1), RangeError);
  assert.throws(() => latLonParaTile(0, 0, 1.5), RangeError);
  assert.throws(() => tileParaLatLon(2, 9, 0), RangeError);
});
