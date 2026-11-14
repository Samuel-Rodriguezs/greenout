import test from 'node:test';
import assert from 'node:assert/strict';
import { mulberry32, criarJogo, virar, passo, posicionarComida } from './snake.js';

test('estado inicial', () => {
  const j = criarJogo(10, 10, mulberry32(1));
  assert.equal(j.cobra.length, 3);
  assert.ok(j.vivo);
  assert.ok(!j.cobra.some((p) => p.x === j.comida.x && p.y === j.comida.y));
});

test('anda para a direita', () => {
  const rng = mulberry32(1);
  const j = passo(criarJogo(10, 10, rng), rng);
  assert.deepEqual(j.cobra[0], { x: 6, y: 5 });
  assert.equal(j.cobra.length, 3);
});

test('não permite reverter direção; permite virar', () => {
  const j = criarJogo(10, 10, mulberry32(1));
  assert.equal(virar(j, 'esquerda'), j);
  assert.equal(virar(j, 'cima').direcao, 'cima');
  assert.throws(() => virar(j, 'x'));
});

test('comer cresce, pontua e muda a comida', () => {
  const rng = mulberry32(3);
  let j = criarJogo(10, 10, rng);
  j = { ...j, comida: { x: 6, y: 5 } };
  j = passo(j, rng);
  assert.equal(j.cobra.length, 4);
  assert.equal(j.pontos, 1);
  assert.notDeepEqual(j.comida, { x: 6, y: 5 });
});

test('bater na parede mata', () => {
  const rng = mulberry32(1);
  let j = criarJogo(6, 6, rng);
  for (let i = 0; i < 5 && j.vivo; i++) j = passo(j, rng);
  assert.ok(!j.vivo);
  assert.equal(passo(j, rng), j);
});

test('bater no próprio corpo mata', () => {
  const rng = mulberry32(1);
  let j = criarJogo(10, 10, rng);
  j = { ...j, comida: null, cobra: [{ x: 5, y: 5 }, { x: 5, y: 6 }, { x: 4, y: 6 }, { x: 4, y: 5 }, { x: 4, y: 4 }, { x: 5, y: 4 }, { x: 6, y: 4 }], direcao: 'cima' };
  j = passo(j, rng);
  assert.ok(!j.vivo);
});

test('perseguir a própria cauda é permitido', () => {
  const rng = mulberry32(1);
  const j = { largura: 5, altura: 5, comida: null, pontos: 0, vivo: true, direcao: 'esquerda',
    cobra: [{ x: 2, y: 2 }, { x: 2, y: 3 }, { x: 1, y: 3 }, { x: 1, y: 2 }] };
  assert.ok(passo(j, rng).vivo);
});

test('comida sem espaço livre retorna null', () => {
  assert.equal(posicionarComida(1, 1, [{ x: 0, y: 0 }], () => 0), null);
});
