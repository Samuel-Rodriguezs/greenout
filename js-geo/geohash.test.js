import test from 'node:test';
import assert from 'node:assert/strict';
import { codifica, decodifica, decodificaBBox, vizinho, vizinhos } from './geohash.js';

test('valores de referência da especificação', () => {
  assert.equal(codifica(57.64911, 10.40744, 11), 'u4pruydqqvj');
  assert.equal(codifica(42.6, -5.6, 5), 'ezs42');
});

test('São Paulo e Rio de Janeiro', () => {
  assert.equal(codifica(-23.5505, -46.6333, 5), '6gyf4');
  assert.equal(codifica(-22.9068, -43.1729, 5), '75cm9');
});

test('decodificação devolve o centro da célula', () => {
  const [lat, lon] = decodifica('ezs42');
  assert.ok(Math.abs(lat - 42.605) < 0.001);
  assert.ok(Math.abs(lon - -5.603) < 0.001);
});

test('ida e volta: o ponto original cai na caixa do hash', () => {
  const h = codifica(-23.5505, -46.6333, 8);
  const b = decodificaBBox(h);
  assert.ok(-23.5505 >= b.latMin && -23.5505 <= b.latMax);
  assert.ok(-46.6333 >= b.lonMin && -46.6333 <= b.lonMax);
  assert.equal(codifica(...decodifica(h), 8), h);
});

test('prefixo = célula contendo a célula filha', () => {
  const h = codifica(48.8566, 2.3522, 9);
  const pai = decodificaBBox(h.slice(0, 5));
  const filho = decodificaBBox(h);
  assert.ok(filho.latMin >= pai.latMin && filho.latMax <= pai.latMax);
  assert.ok(filho.lonMin >= pai.lonMin && filho.lonMax <= pai.lonMax);
});

test('maiúsculas são aceitas na decodificação', () => {
  assert.deepEqual(decodifica('EZS42'), decodifica('ezs42'));
});

test('8 vizinhos distintos, mesmo tamanho, e simetria leste/oeste', () => {
  const v = vizinhos('ezs42');
  const lista = Object.values(v);
  assert.equal(new Set(lista).size, 8);
  assert.ok(lista.every((h) => h.length === 5));
  assert.equal(vizinho(v.e, 'w'), 'ezs42');
  assert.equal(vizinho(v.n, 's'), 'ezs42');
  assert.equal(vizinho(v.ne, 'sw'), 'ezs42');
});

test('vizinho a leste de ezs42 é ezs43', () => {
  assert.equal(vizinho('ezs42', 'e'), 'ezs43');
});

test('longitude dá a volta no antimeridiano', () => {
  const h = codifica(0, 179.99, 4);
  const leste = vizinho(h, 'e');
  assert.ok(decodifica(leste)[1] < 0);
});

test('polos não têm vizinho além deles', () => {
  const polo = codifica(89.99, 10, 3);
  assert.equal(vizinho(polo, 'n'), null);
  assert.notEqual(vizinho(polo, 's'), null);
});

test('entradas inválidas', () => {
  assert.throws(() => codifica(91, 0), RangeError);
  assert.throws(() => codifica(0, 0, 0), RangeError);
  assert.throws(() => decodifica('abca'), RangeError); // 'a' não existe no alfabeto
  assert.throws(() => decodifica(''), TypeError);
  assert.throws(() => vizinho('ezs42', 'x'), RangeError);
});
