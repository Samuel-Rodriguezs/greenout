import test from 'node:test';
import assert from 'node:assert/strict';
import { distanciaHaversine, rumoInicial, destino, pontoMedio, normalizaLon, RAIO_TERRA_M } from './haversine.js';

const dentro = (v, min, max) => assert.ok(v >= min && v <= max, `${v} fora de [${min}, ${max}]`);

const SP = [-23.5505, -46.6333];
const RIO = [-22.9068, -43.1729];
const PARIS = [48.8566, 2.3522];
const LONDRES = [51.5074, -0.1278];
const NY = [40.7128, -74.006];
const LA = [34.0522, -118.2437];

test('São Paulo - Rio de Janeiro ≈ 361 km', () => {
  dentro(distanciaHaversine(...SP, ...RIO) / 1000, 358, 363);
});

test('Paris - Londres ≈ 344 km', () => {
  dentro(distanciaHaversine(...PARIS, ...LONDRES) / 1000, 342, 346);
});

test('Nova York - Los Angeles ≈ 3936 km', () => {
  dentro(distanciaHaversine(...NY, ...LA) / 1000, 3920, 3950);
});

test('distância é simétrica e zero para o mesmo ponto', () => {
  assert.equal(distanciaHaversine(...SP, ...SP), 0);
  assert.equal(distanciaHaversine(...SP, ...RIO), distanciaHaversine(...RIO, ...SP));
});

test('um grau de latitude no equador ≈ 111,2 km; antípodas = meia circunferência', () => {
  dentro(distanciaHaversine(0, 0, 1, 0) / 1000, 111.1, 111.3);
  assert.ok(Math.abs(distanciaHaversine(0, 0, 0, 180) - Math.PI * RAIO_TERRA_M) < 1e-6);
});

test('travessia do antimeridiano usa o caminho curto', () => {
  dentro(distanciaHaversine(0, 179.5, 0, -179.5) / 1000, 111.0, 111.4);
});

test('rumos cardeais', () => {
  assert.equal(rumoInicial(0, 0, 10, 0), 0);
  assert.ok(Math.abs(rumoInicial(0, 0, 0, 10) - 90) < 1e-9);
  assert.ok(Math.abs(rumoInicial(0, 0, -10, 0) - 180) < 1e-9);
  assert.ok(Math.abs(rumoInicial(0, 0, 0, -10) - 270) < 1e-9);
});

test('rumo Rio -> São Paulo aponta para oeste-sudoeste', () => {
  dentro(rumoInicial(...RIO, ...SP), 250, 265);
});

test('destino é inverso de distância + rumo', () => {
  const d = distanciaHaversine(...SP, ...RIO);
  const b = rumoInicial(...SP, ...RIO);
  const [lat, lon] = destino(...SP, b, d);
  assert.ok(Math.abs(lat - RIO[0]) < 1e-6);
  assert.ok(Math.abs(lon - RIO[1]) < 1e-6);
});

test('destino ao norte e cruzando o antimeridiano', () => {
  const [lat, lon] = destino(0, 0, 0, (Math.PI / 2) * RAIO_TERRA_M);
  assert.ok(Math.abs(lat - 90) < 1e-9);
  void lon;
  const [, lon2] = destino(0, 179, 90, 222390);
  assert.ok(lon2 < 0 && lon2 > -180);
});

test('ponto médio no equador e normalização de longitude', () => {
  const [lat, lon] = pontoMedio(0, 0, 0, 90);
  assert.ok(Math.abs(lat) < 1e-9 && Math.abs(lon - 45) < 1e-9);
  assert.equal(normalizaLon(190), -170);
  assert.equal(normalizaLon(-190), 170);
  assert.equal(normalizaLon(180), -180);
});

test('coordenadas inválidas lançam erro', () => {
  assert.throws(() => distanciaHaversine(91, 0, 0, 0), RangeError);
  assert.throws(() => distanciaHaversine(NaN, 0, 0, 0), RangeError);
});
