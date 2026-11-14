import test from 'node:test';
import assert from 'node:assert/strict';
import { areaEsferica, areaCaixaLatLon, areaPoligonoGeoJSON } from './areaEsferica.js';
import { RAIO_TERRA_M } from './haversine.js';

const km2 = (m2) => m2 / 1e6;
const dentro = (v, min, max) => assert.ok(v >= min && v <= max, `${v} fora de [${min}, ${max}]`);

test('Colorado (caixa 37-41N, 109.05-102.05W) ≈ 269 mil km²', () => {
  const co = [[37, -109.05], [37, -102.05], [41, -102.05], [41, -109.05]];
  dentro(km2(areaEsferica(co)), 268000, 270500);
});

test('Chamberlain-Duquette concorda com a fórmula exata em caixas pequenas', () => {
  const caixa = [[-24, -47], [-24, -46], [-23, -46], [-23, -47]];
  const exata = areaCaixaLatLon(-24, -23, -47, -46);
  assert.ok(Math.abs(areaEsferica(caixa) - exata) / exata < 1e-3);
});

test('1 grau x 1 grau no equador ≈ 12 364 km²', () => {
  dentro(km2(areaCaixaLatLon(0, 1, 0, 1)), 12360, 12368);
});

test('orientação do anel não importa; anel fechado é aceito', () => {
  const a = [[0, 0], [0, 2], [2, 2], [2, 0]];
  assert.equal(areaEsferica(a), areaEsferica([...a].reverse()));
  assert.equal(areaEsferica(a), areaEsferica([...a, a[0]]));
});

test('esfera inteira: faixa de lat -90..90 dá 4πR²', () => {
  const total = areaCaixaLatLon(-90, 90, -180, 180);
  assert.ok(Math.abs(total - 4 * Math.PI * RAIO_TERRA_M ** 2) / total < 1e-12);
});

test('polígono que cruza o antimeridiano usa o lado curto', () => {
  const fiji = [[-17, 178], [-17, -179], [-16, -179], [-16, 178]];
  const comum = [[-17, 10], [-17, 13], [-16, 13], [-16, 10]];
  const a = areaEsferica(fiji), b = areaEsferica(comum);
  assert.ok(Math.abs(a - b) / b < 0.01);
});

test('área de GeoJSON Polygon subtrai buracos', () => {
  const ext = [[0, 0], [4, 0], [4, 4], [0, 4], [0, 0]];
  const furo = [[1, 1], [2, 1], [2, 2], [1, 2], [1, 1]];
  const cheia = areaPoligonoGeoJSON([ext]);
  const vazada = areaPoligonoGeoJSON([ext, furo]);
  assert.ok(vazada < cheia);
  assert.ok(Math.abs(cheia - areaCaixaLatLon(0, 4, 0, 4)) / cheia < 5e-3);
  assert.ok(Math.abs((cheia - vazada) - areaCaixaLatLon(1, 2, 1, 2)) / areaCaixaLatLon(1, 2, 1, 2) < 5e-3);
});

test('entradas inválidas', () => {
  assert.throws(() => areaEsferica([[0, 0], [1, 1]]), RangeError);
  assert.throws(() => areaEsferica([[95, 0], [0, 1], [1, 1]]), RangeError);
  assert.throws(() => areaCaixaLatLon(5, 1, 0, 1), RangeError);
});
