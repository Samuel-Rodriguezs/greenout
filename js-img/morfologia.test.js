import test from 'node:test';
import assert from 'node:assert/strict';
import { deCinza } from './imagem.js';
import { erosao, dilatacao, abertura, fechamento, gradienteMorfologico, quadrado, cruz } from './morfologia.js';

const vals = (img) => Array.from({ length: img.largura * img.altura }, (_, i) => img.dados[i * 4]);
// Cria imagem binária a partir de linhas de texto ('#' = 255).
const mapa = (...linhas) => deCinza(linhas[0].length, linhas.length, linhas.join('').split('').map((c) => (c === '#' ? 255 : 0)));
const texto = (img) => {
  const v = vals(img);
  const l = [];
  for (let y = 0; y < img.altura; y++) l.push(v.slice(y * img.largura, (y + 1) * img.largura).map((x) => (x ? '#' : '.')).join(''));
  return l;
};

test('elementos estruturantes', () => {
  assert.equal(quadrado(1).length, 9);
  assert.equal(cruz(1).length, 5);
  assert.equal(cruz(2).length, 9);
});

test('erosão de bloco 3x3 com cruz deixa só o centro', () => {
  const img = mapa('.....', '.###.', '.###.', '.###.', '.....');
  assert.deepEqual(texto(erosao(img, cruz(1))), ['.....', '.....', '..#..', '.....', '.....']);
  assert.deepEqual(texto(erosao(img, quadrado(1))), ['.....', '.....', '..#..', '.....', '.....']);
});

test('dilatação de um ponto com cruz e com quadrado', () => {
  const img = mapa('.....', '.....', '..#..', '.....', '.....');
  assert.deepEqual(texto(dilatacao(img, cruz(1))), ['.....', '..#..', '.###.', '..#..', '.....']);
  assert.deepEqual(texto(dilatacao(img, quadrado(1))), ['.....', '.###.', '.###.', '.###.', '.....']);
});

test('abertura remove ruído isolado e mantém o bloco', () => {
  const img = mapa('#......', '..###..', '..###..', '..###..', '.......');
  assert.deepEqual(texto(abertura(img, quadrado(1))), ['.......', '..###..', '..###..', '..###..', '.......']);
});

test('fechamento preenche buraco de um pixel (borda externa erode como fundo)', () => {
  const img = mapa('#####', '#####', '##.##', '#####', '#####');
  assert.deepEqual(texto(fechamento(img, quadrado(1))), ['.....', '.###.', '.###.', '.###.', '.....']);
});

test('borda da imagem conta como fundo na erosão', () => {
  const img = mapa('###', '###', '###');
  assert.deepEqual(texto(erosao(img, quadrado(1))), ['...', '.#.', '...']);
});

test('gradiente morfológico dá o contorno', () => {
  const img = mapa('.......', '.#####.', '.#####.', '.#####.', '.#####.', '.#####.', '.......');
  const g = texto(gradienteMorfologico(img, quadrado(1)));
  // dilatação (7x7 menos cantos? quadrado->bloco 7x7) - erosão (bloco 3x3)
  assert.equal(g[0], '#######');
  assert.equal(g[3], '##...##');
});
