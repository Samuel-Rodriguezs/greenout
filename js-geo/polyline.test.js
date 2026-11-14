import test from 'node:test';
import assert from 'node:assert/strict';
import { codifica, decodifica } from './polyline.js';

const EXEMPLO = [[38.5, -120.2], [40.7, -120.95], [43.252, -126.453]];
const TEXTO = '_p~iF~ps|U_ulLnnqC_mqNvxq`@';

test('exemplo oficial da documentação do Google', () => {
  assert.equal(codifica(EXEMPLO), TEXTO);
  assert.deepEqual(decodifica(TEXTO), EXEMPLO);
});

test('lista vazia e ponto único', () => {
  assert.equal(codifica([]), '');
  assert.deepEqual(decodifica(''), []);
  assert.deepEqual(decodifica(codifica([[0, 0]])), [[0, 0]]);
  assert.equal(codifica([[0, 0]]), '??');
});

test('ida e volta com coordenadas negativas (São Paulo -> Rio)', () => {
  const rota = [[-23.55052, -46.63331], [-23.0, -45.0], [-22.9068, -43.1729]];
  assert.deepEqual(decodifica(codifica(rota)), rota);
});

test('precisão 6 (OSRM/Valhalla)', () => {
  const p = [[48.856614, 2.352222]];
  assert.deepEqual(decodifica(codifica(p, 6), 6), p);
});

test('valores maiores que 5 bits usam bytes de continuação', () => {
  const p = [[-179.99999, 179.99999]];
  assert.deepEqual(decodifica(codifica(p)), p);
});

test('texto truncado ou com caractere inválido lança erro', () => {
  assert.throws(() => decodifica(TEXTO.slice(0, 7)), RangeError);
  assert.throws(() => decodifica('\u0001abc'), RangeError);
});
