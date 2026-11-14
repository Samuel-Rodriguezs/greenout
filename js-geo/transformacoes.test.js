import test from 'node:test';
import assert from 'node:assert/strict';
import { Mat3, Mat4 } from './transformacoes.js';

const quase = (a, b, eps = 1e-9) => {
  assert.equal(a.length, b.length);
  a.forEach((v, i) => assert.ok(Math.abs(v - b[i]) <= eps, `[${i}] ${v} != ${b[i]}`));
};

test('translação e escala 2D', () => {
  assert.deepEqual(Mat3.translacao(3, -2).aplica([1, 1]), [4, -1]);
  assert.deepEqual(Mat3.escala(2, 3).aplica([1, 1]), [2, 3]);
  assert.deepEqual(Mat3.escala(2).aplica([4, 5]), [8, 10]);
});

test('rotação de 90 graus leva (1,0) a (0,1)', () => {
  quase(Mat3.rotacao(Math.PI / 2).aplica([1, 0]), [0, 1]);
});

test('composição: this * outra aplica outra primeiro', () => {
  const m = Mat3.translacao(10, 0).multiplica(Mat3.escala(2));
  assert.deepEqual(m.aplica([1, 1]), [12, 2]);
  const n = Mat3.escala(2).multiplica(Mat3.translacao(10, 0));
  assert.deepEqual(n.aplica([1, 1]), [22, 2]);
});

test('rotação em torno de um ponto mantém o ponto fixo', () => {
  const m = Mat3.rotacaoEm(Math.PI / 3, 5, 5);
  quase(m.aplica([5, 5]), [5, 5]);
  quase(Mat3.rotacaoEm(Math.PI, 5, 5).aplica([6, 5]), [4, 5]);
});

test('inversa desfaz a transformação (2D)', () => {
  const m = Mat3.translacao(3, 4).multiplica(Mat3.rotacao(0.7)).multiplica(Mat3.escala(2, 0.5));
  const p = [3.3, -1.2];
  quase(m.inversa().aplica(m.aplica(p)), p);
  quase(m.multiplica(m.inversa()).m, Mat3.identidade().m);
});

test('determinante e matriz singular', () => {
  assert.equal(Mat3.escala(2, 3).determinante(), 6);
  assert.ok(Math.abs(Mat3.rotacao(1.1).determinante() - 1) < 1e-12);
  assert.equal(Mat3.reflexaoX().determinante(), -1);
  assert.throws(() => Mat3.escala(0, 1).inversa(), RangeError);
});

test('cisalhamento e transposta', () => {
  assert.deepEqual(Mat3.cisalhamento(2).aplica([1, 3]), [7, 3]);
  assert.deepEqual(Mat3.translacao(1, 2).transposta().m.slice(6), [1, 2, 1]);
});

test('imutabilidade', () => {
  const m = Mat3.identidade();
  assert.ok(Object.isFrozen(m) && Object.isFrozen(m.m));
  m.multiplica(Mat3.escala(5));
  assert.deepEqual([...m.m], [1, 0, 0, 0, 1, 0, 0, 0, 1]);
});

test('3D: translação, escala e rotação em cada eixo', () => {
  assert.deepEqual(Mat4.translacao(1, 2, 3).aplica([0, 0, 0]), [1, 2, 3]);
  assert.deepEqual(Mat4.escala(2).aplica([1, 2, 3]), [2, 4, 6]);
  quase(Mat4.rotacaoZ(Math.PI / 2).aplica([1, 0, 0]), [0, 1, 0]);
  quase(Mat4.rotacaoX(Math.PI / 2).aplica([0, 1, 0]), [0, 0, 1]);
  quase(Mat4.rotacaoY(Math.PI / 2).aplica([0, 0, 1]), [1, 0, 0]);
});

test('3D: rotação em eixo arbitrário coincide com rotação em Z', () => {
  quase(Mat4.rotacaoEixo([0, 0, 7], 0.9).m, Mat4.rotacaoZ(0.9).m);
  assert.throws(() => Mat4.rotacaoEixo([0, 0, 0], 1), RangeError);
});

test('3D: inversa e determinante', () => {
  const m = Mat4.translacao(1, -2, 3).multiplica(Mat4.rotacaoEixo([1, 1, 0], 0.6)).multiplica(Mat4.escala(2, 3, 4));
  const p = [0.5, 1.5, -2];
  quase(m.inversa().aplica(m.aplica(p)), p);
  assert.ok(Math.abs(m.determinante() - 24) < 1e-9);
});

test('dimensões incompatíveis e tamanho errado lançam erro', () => {
  assert.throws(() => Mat3.identidade().multiplica(Mat4.identidade()), RangeError);
  assert.throws(() => new Mat3([1, 2, 3]), RangeError);
});
