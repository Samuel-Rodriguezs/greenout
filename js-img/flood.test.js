import test from 'node:test';
import assert from 'node:assert/strict';
import { deCinza, obter } from './imagem.js';
import { preencher } from './flood.js';

const vals = (img) => Array.from({ length: img.largura * img.altura }, (_, i) => img.dados[i * 4]);
const mapa = (...linhas) => deCinza(linhas[0].length, linhas.length, linhas.join('').split('').map((c) => (c === '#' ? 255 : 0)));
const texto = (img) => {
  const v = vals(img);
  return Array.from({ length: img.altura }, (_, y) => v.slice(y * img.largura, (y + 1) * img.largura).map((n) => (n === 255 ? '#' : n === 128 ? 'o' : '.')).join(''));
};
const cinza = [128, 128, 128, 255];

test('preenche região delimitada por parede', () => {
  const img = mapa('..#..', '..#..', '..#..', '..#..');
  const { imagem, preenchidos } = preencher(img, 0, 0, cinza);
  assert.equal(preenchidos, 8);
  assert.deepEqual(texto(imagem), ['oo#..', 'oo#..', 'oo#..', 'oo#..']);
  assert.deepEqual(texto(img)[0], '..#..'); // original intacta
});

test('4-conexo não atravessa diagonal; 8-conexo atravessa', () => {
  const img = mapa('.#.', '#.#', '.#.');
  assert.equal(preencher(img, 1, 1, cinza, { conectividade: 4 }).preenchidos, 1);
  const r8 = preencher(img, 1, 1, cinza, { conectividade: 8 });
  assert.equal(r8.preenchidos, 5);
  assert.deepEqual(texto(r8.imagem), ['o#o', '#o#', 'o#o']);
});

test('forma em espiral/C é preenchida inteira', () => {
  const img = mapa('....', '.##.', '.#..', '....');
  const { preenchidos } = preencher(img, 0, 0, cinza);
  assert.equal(preenchidos, 13);
});

test('tolerância junta tons próximos', () => {
  const img = deCinza(4, 1, [100, 105, 110, 200]);
  assert.equal(preencher(img, 0, 0, cinza, { tolerancia: 0 }).preenchidos, 1);
  assert.equal(preencher(img, 0, 0, cinza, { tolerancia: 5 }).preenchidos, 2);
  assert.equal(preencher(img, 0, 0, cinza, { tolerancia: 10 }).preenchidos, 3);
});

test('semente inválida e cor idêntica', () => {
  const img = mapa('..', '..');
  assert.throws(() => preencher(img, 2, 0, cinza), RangeError);
  assert.throws(() => preencher(img, 0, 0, cinza, { conectividade: 5 }));
  assert.deepEqual(obter(preencher(img, 1, 1, [0, 0, 0, 255]).imagem, 0, 0), [0, 0, 0, 255]);
});
