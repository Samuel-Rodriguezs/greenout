import test from 'node:test';
import assert from 'node:assert/strict';
import { BloomFilter } from './bloomFilter.js';

test('filtro vazio nega tudo', () => {
  const b = new BloomFilter();
  assert.equal(b.talvezTenha('x'), false);
  assert.equal(b.taxaFalsoPositivo, 0);
});
test('nunca há falso negativo', () => {
  const b = BloomFilter.para(500, 0.01);
  for (let i = 0; i < 500; i++) b.adicionar(`item-${i}`);
  for (let i = 0; i < 500; i++) assert.equal(b.talvezTenha(`item-${i}`), true);
  assert.equal(b.inseridos, 500);
});
test('falsos positivos ficam perto da taxa alvo', () => {
  const b = BloomFilter.para(1000, 0.01);
  for (let i = 0; i < 1000; i++) b.adicionar(`in-${i}`);
  let fp = 0;
  for (let i = 0; i < 10000; i++) if (b.talvezTenha(`out-${i}`)) fp++;
  assert.ok(fp / 10000 < 0.03, `taxa alta demais: ${fp / 10000}`);
  assert.ok(b.taxaFalsoPositivo < 0.03);
});
test('aceita números e tipos misturados', () => {
  const b = new BloomFilter(256, 3).adicionar(42).adicionar('42x');
  assert.equal(b.talvezTenha(42), true);
  assert.equal(b.talvezTenha('42x'), true);
});
test('parâmetros inválidos', () => {
  assert.throws(() => new BloomFilter(0, 1), RangeError);
  assert.throws(() => new BloomFilter(8, 0), RangeError);
  assert.throws(() => new BloomFilter(1.5, 1), RangeError);
});
test('filtro minúsculo satura mas mantém garantia', () => {
  const b = new BloomFilter(8, 2);
  for (let i = 0; i < 100; i++) b.adicionar(i);
  for (let i = 0; i < 100; i++) assert.equal(b.talvezTenha(i), true);
});
