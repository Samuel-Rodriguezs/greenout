import { test } from 'node:test';
import assert from 'node:assert/strict';
import { ehEmail, ehURL, ehCPF, ehCNPJ } from './validadores.js';

test('email', () => {
  assert.ok(ehEmail('ana.silva+x@exemplo.com.br'));
  for (const ruim of ['ana@', '@x.com', 'a b@x.com', 'a@x', 'a@x..com', 42]) assert.ok(!ehEmail(ruim), String(ruim));
});
test('url', () => {
  assert.ok(ehURL('https://exemplo.com/a?b=1'));
  assert.ok(!ehURL('exemplo.com'));
  assert.ok(!ehURL('javascript:alert(1)'));
  assert.ok(ehURL('ftp://x.org', ['ftp:']));
});
test('cpf', () => {
  assert.ok(ehCPF('529.982.247-25'));
  assert.ok(ehCPF('52998224725'));
  assert.ok(!ehCPF('529.982.247-24'));
  assert.ok(!ehCPF('111.111.111-11'));
  assert.ok(!ehCPF('123'));
});
test('cnpj', () => {
  assert.ok(ehCNPJ('11.222.333/0001-81'));
  assert.ok(!ehCNPJ('11.222.333/0001-82'));
  assert.ok(!ehCNPJ('00000000000000'));
});
