import test from 'node:test';
import assert from 'node:assert/strict';
import { rules, createValidator, validateField } from './formValidation.js';

const v = createValidator({
  nome: [rules.required(), rules.minLength(3)],
  email: [rules.required(), rules.email()],
  idade: [rules.min(18), rules.max(120)],
  senha: [rules.minLength(6)],
  confirma: [rules.matches('senha')],
  plano: [rules.oneOf(['free', 'pro'])],
});

test('formulário válido', () => {
  const r = v.validate({ nome: 'Ana', email: 'a@b.co', idade: '30', senha: 'abcdef', confirma: 'abcdef', plano: 'pro' });
  assert.deepEqual(r, { valid: true, errors: {} });
});

test('coleta múltiplos erros por campo', () => {
  const r = v.validate({ nome: '', email: 'x', idade: 10, senha: 'a', confirma: 'b', plano: 'zzz' });
  assert.equal(r.valid, false);
  assert.deepEqual(r.errors.nome, ['Campo obrigatório', 'Mínimo de 3 caracteres']);
  assert.deepEqual(r.errors.email, ['E-mail inválido']);
  assert.deepEqual(r.errors.idade, ['Valor mínimo 18']);
  assert.deepEqual(r.errors.confirma, ['Campos não conferem']);
  assert.deepEqual(r.errors.plano, ['Valor não permitido']);
});

test('campos opcionais vazios passam em email/min', () => {
  assert.deepEqual(validateField('', [rules.email(), rules.min(5)]), []);
});

test('pattern e maxLength com mensagens custom', () => {
  assert.deepEqual(validateField('abc', [rules.pattern(/^\d+$/, 'só dígitos'), rules.maxLength(2, 'longo')]), ['só dígitos', 'longo']);
});

test('required em arrays', () => {
  assert.deepEqual(validateField([], [rules.required('vazio')]), ['vazio']);
});

test('validateAsync com regra assíncrona', async () => {
  const av = createValidator({ user: [async (val) => (val === 'admin' ? 'em uso' : null)] });
  assert.deepEqual(await av.validateAsync({ user: 'admin' }), { valid: false, errors: { user: ['em uso'] } });
  assert.equal((await av.validateAsync({ user: 'novo' })).valid, true);
});
