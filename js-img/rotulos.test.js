import test from 'node:test';
import assert from 'node:assert/strict';
import { deCinza } from './imagem.js';
import { rotular, caixas } from './rotulos.js';

const mapa = (...linhas) => deCinza(linhas[0].length, linhas.length, linhas.join('').split('').map((c) => (c === '#' ? 255 : 0)));
const grade = (r) => {
  const l = [];
  for (let y = 0; y < r.altura; y++) l.push(Array.from(r.rotulos.subarray(y * r.largura, (y + 1) * r.largura)).join(''));
  return l;
};

test('dois blocos separados 5x5', () => {
  const r = rotular(mapa('##...', '##...', '.....', '...##', '...##'));
  assert.equal(r.quantidade, 2);
  assert.deepEqual(grade(r), ['11000', '11000', '00000', '00022', '00022']);
  assert.deepEqual(r.areas, [0, 4, 4]);
});

test('diagonal: 4-conexo separa, 8-conexo une', () => {
  const img = mapa('#..', '.#.', '..#');
  assert.equal(rotular(img, 4).quantidade, 3);
  const r8 = rotular(img, 8);
  assert.equal(r8.quantidade, 1);
  assert.deepEqual(r8.areas, [0, 3]);
});

test('forma em U exige união de rótulos provisórios', () => {
  const r = rotular(mapa('#.#', '#.#', '###'));
  assert.equal(r.quantidade, 1);
  assert.deepEqual(grade(r), ['101', '101', '111']);
  assert.equal(r.areas[1], 7);
});

test('imagem sem primeiro plano', () => {
  const r = rotular(mapa('...', '...'));
  assert.equal(r.quantidade, 0);
  assert.deepEqual(r.areas, [0]);
});

test('caixas delimitadoras e conectividade inválida', () => {
  const r = rotular(mapa('##....', '#...##', '....##', '#.....'));
  assert.deepEqual(caixas(r), [
    { rotulo: 1, x0: 0, y0: 0, x1: 1, y1: 1, area: 3 },
    { rotulo: 2, x0: 4, y0: 1, x1: 5, y1: 2, area: 4 },
    { rotulo: 3, x0: 0, y0: 3, x1: 0, y1: 3, area: 1 },
  ]);
  assert.throws(() => rotular(mapa('#'), 6));
});
