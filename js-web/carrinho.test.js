import test from 'node:test';
import assert from 'node:assert/strict';
import { createCarrinho } from './carrinho.js';

const cupons = {
  DEZ: { tipo: 'percentual', valor: 10, cumulativo: true },
  CINCO: { tipo: 'fixo', valor: 500, cumulativo: true },
  GRANDE: { tipo: 'percentual', valor: 50, max: 2000, minimo: 10000 },
  VELHO: { tipo: 'fixo', valor: 100, expira: '2000-01-01', cumulativo: true },
};
const frete = ({ subtotal }) => (subtotal >= 20000 ? 0 : 1500);

function novo() {
  const c = createCarrinho({ cupons, frete });
  c.adicionar({ sku: 'A', nome: 'Camiseta', preco: 5000 }, 2);
  c.adicionar({ sku: 'B', nome: 'Boné', preco: 2990 });
  return c;
}

test('subtotal e frete', () => {
  const c = novo();
  assert.deepEqual(c.totais(), { subtotal: 12990, descontos: [], desconto: 0, frete: 1500, total: 14490 });
  assert.equal(c.quantidade, 3);
});

test('adicionar mesmo sku soma quantidades', () => {
  const c = novo();
  c.adicionar({ sku: 'A', nome: 'Camiseta', preco: 5000 });
  assert.equal(c.itens().find((i) => i.sku === 'A').qtd, 3);
});

test('alterar e remover', () => {
  const c = novo();
  c.alterarQtd('B', 3);
  assert.equal(c.totais().subtotal, 10000 + 8970);
  c.alterarQtd('B', 0);
  c.remover('A');
  assert.equal(c.vazio(), true);
  assert.equal(c.totais().frete, 0);
  assert.throws(() => c.alterarQtd('Z', 1));
});

test('cupons cumulativos aplicados em sequência', () => {
  const c = novo();
  c.aplicarCupom('dez');
  c.aplicarCupom('CINCO');
  const t = c.totais();
  assert.deepEqual(t.descontos, [{ codigo: 'DEZ', valor: 1299 }, { codigo: 'CINCO', valor: 500 }]);
  assert.equal(t.total, 12990 - 1799 + 1500);
});

test('cupom não cumulativo, com teto e mínimo', () => {
  const c = novo();
  c.aplicarCupom('GRANDE');
  assert.equal(c.totais().desconto, 2000);
  assert.throws(() => c.aplicarCupom('DEZ'), /cumulativo/);
  const pequeno = createCarrinho({ cupons, frete });
  pequeno.adicionar({ sku: 'x', preco: 1000 });
  assert.throws(() => pequeno.aplicarCupom('GRANDE'), /mínimo/);
});

test('cupom inválido, repetido ou expirado', () => {
  const c = novo();
  assert.throws(() => c.aplicarCupom('NADA'), /inválido/);
  c.aplicarCupom('DEZ');
  assert.throws(() => c.aplicarCupom('DEZ'), /já aplicado/);
  assert.throws(() => c.aplicarCupom('VELHO'), /expirado/);
});

test('desconto nunca passa do subtotal e frete grátis acima de 200', () => {
  const c = createCarrinho({ cupons: { TUDO: { tipo: 'fixo', valor: 99999, cumulativo: true } }, frete });
  c.adicionar({ sku: 'a', preco: 1000 });
  c.aplicarCupom('TUDO');
  assert.deepEqual([c.totais().total, c.totais().frete], [0, 0]);
  const g = novo();
  g.adicionar({ sku: 'C', preco: 10000 });
  assert.equal(g.totais().frete, 0);
});

test('remover cupom e validação de preço', () => {
  const c = novo();
  c.aplicarCupom('DEZ');
  c.removerCupom('dez');
  assert.equal(c.totais().desconto, 0);
  assert.throws(() => c.adicionar({ sku: 'q', preco: 9.9 }), /centavos/);
  assert.throws(() => c.adicionar({ sku: 'q', preco: 1 }, 0), /quantidade/);
});
