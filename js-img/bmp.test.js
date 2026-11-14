import test from 'node:test';
import assert from 'node:assert/strict';
import { dePixels, igual } from './imagem.js';
import { codificarBMP, decodificarBMP } from './bmp.js';

// 3x2: linha de cima R G B ; linha de baixo W K cinza
const img = dePixels(3, 2, [
  [255, 0, 0], [0, 255, 0], [0, 0, 255],
  [255, 255, 255], [0, 0, 0], [10, 20, 30],
]);

test('cabeçalho e tamanhos de um BMP 3x2', () => {
  const b = codificarBMP(img);
  const v = new DataView(b.buffer);
  // linha = 9 bytes -> 12 com padding ; dados = 24 ; arquivo = 54 + 24
  assert.equal(b.length, 78);
  assert.equal(String.fromCharCode(b[0], b[1]), 'BM');
  assert.equal(v.getUint32(2, true), 78);
  assert.equal(v.getUint32(10, true), 54);
  assert.equal(v.getUint32(14, true), 40);
  assert.equal(v.getInt32(18, true), 3);
  assert.equal(v.getInt32(22, true), 2);
  assert.equal(v.getUint16(28, true), 24);
  assert.equal(v.getUint32(34, true), 24);
});

test('pixels: linhas de baixo para cima, BGR, padding zerado', () => {
  const b = codificarBMP(img);
  // primeira linha gravada é a de baixo: W K cinza em BGR
  assert.deepEqual(Array.from(b.subarray(54, 66)), [255, 255, 255, 0, 0, 0, 30, 20, 10, 0, 0, 0]);
  // depois a de cima: R G B em BGR
  assert.deepEqual(Array.from(b.subarray(66, 78)), [0, 0, 255, 0, 255, 0, 255, 0, 0, 0, 0, 0]);
});

test('ida e volta preserva a imagem (larguras com e sem padding)', () => {
  assert.ok(igual(decodificarBMP(codificarBMP(img)), img));
  const quatro = dePixels(4, 1, [[1, 2, 3], [4, 5, 6], [7, 8, 9], [10, 11, 12]]);
  assert.equal(codificarBMP(quatro).length, 54 + 12);
  assert.ok(igual(decodificarBMP(codificarBMP(quatro)), quatro));
});

test('decodifica BMP top-down (altura negativa)', () => {
  const b = codificarBMP(img);
  // reconstrói como top-down: inverte a ordem das linhas e a altura
  const td = new Uint8Array(b);
  td.set(b.subarray(66, 78), 54);
  td.set(b.subarray(54, 66), 66);
  new DataView(td.buffer).setInt32(22, -2, true);
  assert.ok(igual(decodificarBMP(td), img));
});

test('erros', () => {
  assert.throws(() => decodificarBMP(new Uint8Array(60)), /não é um BMP/);
  const b = codificarBMP(img);
  assert.throws(() => decodificarBMP(b.subarray(0, 60)), /truncado/);
  const c = new Uint8Array(b);
  c[28] = 32;
  assert.throws(() => decodificarBMP(c), /24 bits/);
});
