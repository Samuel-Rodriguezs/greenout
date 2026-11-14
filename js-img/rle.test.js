import test from 'node:test';
import assert from 'node:assert/strict';
import { deCinza, igual } from './imagem.js';
import { codificarRLE, decodificarRLE, runsPorLinha, deRuns, rleImagem } from './rle.js';

test('RLE de bytes: exemplo à mão', () => {
  assert.deepEqual(Array.from(codificarRLE(Uint8Array.from([7, 7, 7, 1, 2, 2]))), [3, 7, 1, 1, 2, 2]);
  assert.deepEqual(Array.from(codificarRLE([])), []);
});

test('runs maiores que 255 são divididos', () => {
  const longo = new Uint8Array(300).fill(9);
  assert.deepEqual(Array.from(codificarRLE(longo)), [255, 9, 45, 9]);
  assert.deepEqual(Array.from(decodificarRLE(codificarRLE(longo))), Array.from(longo));
});

test('ida e volta com dados variados', () => {
  const d = Uint8Array.from([0, 0, 1, 2, 3, 3, 3, 3, 0, 255, 255]);
  assert.deepEqual(Array.from(decodificarRLE(codificarRLE(d))), Array.from(d));
});

test('decodificação rejeita entradas inválidas', () => {
  assert.throws(() => decodificarRLE(Uint8Array.from([1, 2, 3])), /ímpar/);
  assert.throws(() => decodificarRLE(Uint8Array.from([0, 5])), /zero/);
});

test('runs por linha em imagem binária 5x3', () => {
  const g = deCinza(5, 3, [0, 0, 255, 255, 255, 255, 255, 255, 255, 255, 0, 255, 0, 255, 0]);
  const r = runsPorLinha(g);
  assert.deepEqual(r[0], [{ valor: 0, comprimento: 2 }, { valor: 1, comprimento: 3 }]);
  assert.deepEqual(r[1], [{ valor: 1, comprimento: 5 }]);
  assert.deepEqual(r[2], [
    { valor: 0, comprimento: 1 }, { valor: 1, comprimento: 1 }, { valor: 0, comprimento: 1 },
    { valor: 1, comprimento: 1 }, { valor: 0, comprimento: 1 },
  ]);
});

test('deRuns reconstrói a imagem e valida cobertura', () => {
  const g = deCinza(5, 3, [0, 0, 255, 255, 255, 255, 255, 255, 255, 255, 0, 255, 0, 255, 0]);
  assert.ok(igual(deRuns(5, runsPorLinha(g)), g));
  assert.throws(() => deRuns(3, [[{ valor: 1, comprimento: 2 }]]), /não cobrem/);
  assert.throws(() => deRuns(2, [[{ valor: 1, comprimento: 3 }]]), /excedem/);
});

test('rleImagem comprime áreas planas', () => {
  const g = deCinza(4, 2, [5, 5, 5, 5, 5, 5, 9, 9]);
  assert.deepEqual(Array.from(rleImagem(g)), [6, 5, 2, 9]);
});
