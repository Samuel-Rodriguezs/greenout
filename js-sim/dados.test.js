import test from 'node:test';
import assert from 'node:assert/strict';
import { mulberry32, parse, rolar, minimo, maximo, media } from './dados.js';

test('parse de 2d6+3', () => {
  assert.deepEqual(parse('2d6+3'), [
    { sinal: 1, tipo: 'dado', qtd: 2, faces: 6 },
    { sinal: 1, tipo: 'const', valor: 3 },
  ]);
});

test('parse: d20 implícito, espaços, subtração, kh/kl', () => {
  assert.deepEqual(parse(' d20 '), [{ sinal: 1, tipo: 'dado', qtd: 1, faces: 20 }]);
  assert.deepEqual(parse('1d8 - 2'), [
    { sinal: 1, tipo: 'dado', qtd: 1, faces: 8 },
    { sinal: -1, tipo: 'const', valor: 2 },
  ]);
  assert.deepEqual(parse('4d6kh3')[0], { sinal: 1, tipo: 'dado', qtd: 4, faces: 6, manter: 3, quais: 'maiores' });
  assert.equal(parse('2D20KL1')[0].quais, 'menores');
});

test('parse rejeita expressões inválidas', () => {
  for (const ruim of ['', 'abc', '2d', 'd1', '2d6+', '+', '0d6', '4d6kh5', '3d6kh0', '2d6++3']) {
    assert.throws(() => parse(ruim), undefined, ruim);
  }
});

test('rolagem é determinística e fica dentro dos limites', () => {
  const a = rolar('2d6+3', mulberry32(1));
  const b = rolar('2d6+3', mulberry32(1));
  assert.deepEqual(a, b);
  assert.ok(a.total >= 5 && a.total <= 15);
  assert.equal(a.detalhes[0].rolagens.length, 2);
});

test('rng controlado produz valores exatos', () => {
  assert.equal(rolar('1d6', () => 0).total, 1);
  assert.equal(rolar('1d6', () => 0.999).total, 6);
  assert.equal(rolar('2d6+3', () => 0.999).total, 15);
  assert.equal(rolar('1d4-1d4', () => 0.5).total, 0);
});

test('kh mantém os maiores e kl os menores', () => {
  const seq = [0, 0.99, 0.5, 0.2]; // em d6: 1, 6, 4, 2
  let i = 0;
  const rng = () => seq[i++ % seq.length];
  const kh = rolar('4d6kh3', rng);
  assert.deepEqual(kh.detalhes[0].rolagens, [1, 6, 4, 2]);
  assert.deepEqual(kh.detalhes[0].mantidas, [6, 4, 2]);
  assert.equal(kh.total, 12);
  i = 0;
  assert.equal(rolar('4d6kl2', rng).total, 3);
});

test('mínimo, máximo e média', () => {
  assert.equal(minimo('2d6+3'), 5);
  assert.equal(maximo('2d6+3'), 15);
  assert.equal(minimo('1d8-2'), -1);
  assert.equal(maximo('1d8-1d4'), 7);
  assert.equal(minimo('1d8-1d4'), -3);
  assert.equal(minimo('4d6kh3'), 3);
  assert.equal(maximo('4d6kh3'), 18);
  assert.equal(media('2d6+3'), 10);
  assert.throws(() => media('4d6kh3'));
});

test('média empírica de 2d6 converge para 7', () => {
  const rng = mulberry32(31337);
  let soma = 0;
  const n = 20000;
  for (let i = 0; i < n; i++) soma += rolar('2d6', rng).total;
  assert.ok(Math.abs(soma / n - 7) < 0.1);
});
