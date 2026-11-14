import test from 'node:test';
import assert from 'node:assert/strict';
import { dePixels, obter } from './imagem.js';
import { luma, paraCinza, planoLuma, mediaCanais } from './cinza.js';

const cores = dePixels(3, 3, [
  [255, 0, 0], [0, 255, 0], [0, 0, 255],
  [255, 255, 255], [0, 0, 0], [100, 150, 200],
  [255, 255, 0], [0, 255, 255], [128, 128, 128],
]);

test('BT.601 em cores primárias', () => {
  const g = paraCinza(cores, 'bt601');
  // 0.299*255=76.2 ; 0.587*255=149.7 ; 0.114*255=29.07
  assert.equal(obter(g, 0, 0)[0], 76);
  assert.equal(obter(g, 1, 0)[0], 150);
  assert.equal(obter(g, 2, 0)[0], 29);
  assert.equal(obter(g, 0, 1)[0], 255);
  assert.equal(obter(g, 1, 1)[0], 0);
});

test('BT.709 em cores primárias', () => {
  const g = paraCinza(cores, 'bt709');
  // 0.2126*255=54.2 ; 0.7152*255=182.4 ; 0.0722*255=18.4
  assert.equal(obter(g, 0, 0)[0], 54);
  assert.equal(obter(g, 1, 0)[0], 182);
  assert.equal(obter(g, 2, 0)[0], 18);
});

test('pixel misto (100,150,200)', () => {
  // 601: 29.9+88.05+22.8 = 140.75 -> 141 ; 709: 21.26+107.28+14.44 = 142.98 -> 143
  assert.equal(obter(paraCinza(cores, 'bt601'), 2, 1)[0], 141);
  assert.equal(obter(paraCinza(cores, 'bt709'), 2, 1)[0], 143);
});

test('cinza puro permanece e canais ficam iguais; alfa preservado', () => {
  const img = dePixels(1, 2, [[128, 128, 128, 77], [10, 200, 30, 5]]);
  const g = paraCinza(img);
  assert.equal(obter(g, 0, 0)[0], 128);
  assert.equal(obter(g, 0, 0)[3], 77);
  const p = obter(g, 0, 1);
  assert.ok(p[0] === p[1] && p[1] === p[2]);
  assert.equal(p[3], 5);
});

test('luma, planoLuma e fórmula inválida', () => {
  assert.ok(Math.abs(luma(255, 255, 255, 'bt709') - 255) < 1e-9);
  assert.equal(planoLuma(cores).length, 9);
  assert.throws(() => luma(1, 1, 1, 'xyz'));
});

test('mediaCanais', () => {
  assert.equal(obter(mediaCanais(cores), 2, 1)[0], 150);
});
