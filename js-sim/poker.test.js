import test from 'node:test';
import assert from 'node:assert/strict';
import {
  mulberry32, criarBaralho, embaralhar, distribuir, parseCarta, parseMao, formatarCarta,
  avaliarMao, compararMaos, melhorMao,
} from './poker.js';

const nome = (txt) => avaliarMao(parseMao(txt)).nome;

test('baralho tem 52 cartas únicas', () => {
  const b = criarBaralho();
  assert.equal(b.length, 52);
  assert.equal(new Set(b.map(formatarCarta)).size, 52);
});

test('embaralhar é determinístico e não muta', () => {
  const b = criarBaralho();
  const a = embaralhar(b, mulberry32(3));
  assert.deepEqual(a, embaralhar(b, mulberry32(3)));
  assert.notDeepEqual(a, b);
  assert.deepEqual(a.map(formatarCarta).sort(), b.map(formatarCarta).sort());
  const { mao, resto } = distribuir(a, 5);
  assert.equal(mao.length, 5);
  assert.equal(resto.length, 47);
  assert.throws(() => distribuir(a, 53));
});

test('parseCarta', () => {
  assert.deepEqual(parseCarta('As'), { valor: 14, naipe: 's' });
  assert.deepEqual(parseCarta('10h'), { valor: 10, naipe: 'h' });
  assert.deepEqual(parseCarta('Td'), { valor: 10, naipe: 'd' });
  assert.equal(formatarCarta(parseCarta('Kc')), 'Kc');
  assert.throws(() => parseCarta('1s'));
  assert.throws(() => parseCarta('Ax'));
});

test('reconhece todas as categorias', () => {
  assert.equal(nome('Ah Kd 9s 5c 2d'), 'Carta alta');
  assert.equal(nome('Ah Ad 9s 5c 2d'), 'Par');
  assert.equal(nome('Ah Ad 9s 9c 2d'), 'Dois pares');
  assert.equal(nome('Ah Ad As 9c 2d'), 'Trinca');
  assert.equal(nome('5h 6d 7s 8c 9d'), 'Sequência');
  assert.equal(nome('2h 6h 9h Jh Kh'), 'Flush');
  assert.equal(nome('3h 3d 3s 9c 9d'), 'Full house');
  assert.equal(nome('7h 7d 7s 7c 2d'), 'Quadra');
  assert.equal(nome('5h 6h 7h 8h 9h'), 'Straight flush');
  assert.equal(nome('Th Jh Qh Kh Ah'), 'Royal flush');
});

test('roda A-2-3-4-5 é sequência baixa', () => {
  const roda = avaliarMao(parseMao('Ah 2d 3s 4c 5d'));
  assert.equal(roda.nome, 'Sequência');
  assert.deepEqual(roda.desempate, [5]);
  assert.ok(compararMaos(parseMao('2h 3d 4s 5c 6d'), parseMao('Ah 2d 3s 4c 5d')) > 0);
  assert.equal(nome('Ah 2h 3h 4h 5h'), 'Straight flush');
  assert.equal(nome('Qh Kd As 2c 3d'), 'Carta alta'); // não dá a volta
});

test('desempates', () => {
  assert.ok(compararMaos(parseMao('Ah Ad 9s 5c 2d'), parseMao('Kh Kd As Qc Jd')) > 0); // par de A > par de K
  assert.ok(compararMaos(parseMao('Ah Ad 9s 5c 2d'), parseMao('As Ac 8s 5d 2h')) > 0); // kicker 9 > 8
  assert.ok(compararMaos(parseMao('Ah Ad 9s 9c 2d'), parseMao('Kh Kd Qs Qc Ad')) > 0); // dois pares
  assert.ok(compararMaos(parseMao('3h 3d 3s 2c 2d'), parseMao('2h 2s 2d Ac Ad')) > 0); // full
  assert.equal(compararMaos(parseMao('Ah Kd 9s 5c 2d'), parseMao('As Kc 9d 5h 2c')), 0);
  assert.ok(compararMaos(parseMao('7h 7d 7s 7c 2d'), parseMao('Ah Ad As Ac Kd')) < 0);
});

test('categoria superior sempre vence', () => {
  assert.ok(compararMaos(parseMao('2h 6h 9h Jh Kh'), parseMao('5h 6d 7s 8c 9d')) > 0);
  assert.ok(compararMaos(parseMao('Ah Ad 9s 9c 2d'), parseMao('Kh Kd Ks 9c 2d')) < 0);
});

test('melhorMao entre 7 cartas', () => {
  const m = melhorMao(parseMao('Ah Kh Qh Jh 2c 2d Th'));
  assert.equal(m.avaliacao.nome, 'Royal flush');
  const f = melhorMao(parseMao('2h 2d 2s 9c 9d 4h Kc'));
  assert.equal(f.avaliacao.nome, 'Full house');
  assert.equal(melhorMao(parseMao('Ah 2d 3s 4c 5d')).cartas.length, 5);
  assert.throws(() => melhorMao(parseMao('Ah 2d 3s 4c')));
  assert.throws(() => avaliarMao(parseMao('Ah 2d 3s 4c')));
});

test('frequência de pares em mãos aleatórias é plausível', () => {
  const rng = mulberry32(2025);
  let pares = 0;
  const n = 4000;
  for (let i = 0; i < n; i++) {
    const { mao } = distribuir(embaralhar(criarBaralho(), rng), 5);
    if (avaliarMao(mao).categoria === 1) pares++;
  }
  const p = pares / n; // teórico ~ 42,26%
  assert.ok(p > 0.38 && p < 0.47);
});
