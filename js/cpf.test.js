import { test } from 'node:test';
import assert from 'node:assert/strict';
import { validarCpf, formatarCpf, completarCpf, limparCpf } from './cpf.js';

test('CPFs válidos conhecidos, com e sem máscara', () => {
  assert.ok(validarCpf('52998224725'));
  assert.ok(validarCpf('529.982.247-25'));
  assert.ok(validarCpf('11144477735'));
});

test('dígito verificador errado', () => {
  assert.ok(!validarCpf('52998224724'));
  assert.ok(!validarCpf('52998224735'));
});

test('sequências repetidas são inválidas', () => {
  for (let d = 0; d <= 9; d++) assert.ok(!validarCpf(String(d).repeat(11)));
});

test('tamanho e caracteres inválidos', () => {
  assert.ok(!validarCpf(''));
  assert.ok(!validarCpf('1234567890'));
  assert.ok(!validarCpf('529982247255'));
  assert.ok(!validarCpf('529.982.24725'));
  assert.ok(!validarCpf('5299822472a'));
  assert.ok(!validarCpf(52998224725));
  assert.ok(!validarCpf(null));
});

test('completarCpf gera dígitos que validam', () => {
  assert.equal(completarCpf('529982247'), '52998224725');
  assert.equal(completarCpf('111444777'), '11144477735');
  for (const base of ['123456789', '000000001', '987654321']) {
    assert.ok(validarCpf(completarCpf(base)));
  }
});

test('formatarCpf e limparCpf', () => {
  assert.equal(formatarCpf('52998224725'), '529.982.247-25');
  assert.equal(limparCpf('529.982.247-25'), '52998224725');
  assert.throws(() => formatarCpf('123'), RangeError);
  assert.throws(() => completarCpf('12'), RangeError);
});
