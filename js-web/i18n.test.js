import test from 'node:test';
import assert from 'node:assert/strict';
import { createI18n } from './i18n.js';

const messages = {
  'pt-BR': {
    ola: 'Olá, {{nome}}!',
    itens: { zero: 'Nenhum item', one: '{{count}} item', other: '{{count}} itens' },
    menu: { sair: 'Sair' },
  },
  en: { hello: 'Hello', menu: { sair: 'Logout', so_en: 'Only EN' } },
  ru: { dias: { one: '{{count}} день', few: '{{count}} дня', many: '{{count}} дней', other: '{{count}} дня' } },
};

test('interpolação', () => {
  const i = createI18n({ messages });
  assert.equal(i.t('ola', { nome: 'Ana' }), 'Olá, Ana!');
  assert.equal(i.t('ola'), 'Olá, {{nome}}!');
});

test('pluralização pt-BR com zero', () => {
  const i = createI18n({ messages });
  assert.equal(i.t('itens', { count: 0 }), 'Nenhum item');
  assert.equal(i.t('itens', { count: 1 }), '1 item');
  assert.equal(i.t('itens', { count: 1500 }), '1.500 itens');
});

test('pluralização com várias categorias (ru)', () => {
  const i = createI18n({ locale: 'ru', messages });
  assert.equal(i.t('dias', { count: 1 }), '1 день');
  assert.equal(i.t('dias', { count: 3 }), '3 дня');
  assert.equal(i.t('dias', { count: 5 }), '5 дней');
});

test('chaves aninhadas e fallback de idioma', () => {
  const i = createI18n({ messages });
  assert.equal(i.t('menu.sair'), 'Sair');
  assert.equal(i.t('menu.so_en'), 'Only EN');
  assert.equal(i.t('hello'), 'Hello');
  assert.equal(i.t('nao.existe'), 'nao.existe');
});

test('troca de locale e addMessages', () => {
  const i = createI18n({ messages });
  i.setLocale('en');
  assert.equal(i.t('menu.sair'), 'Logout');
  i.addMessages('en', { extra: 'Extra {{n}}' });
  assert.equal(i.t('extra', { n: 2 }), 'Extra 2');
  assert.equal(i.has('extra'), true);
  assert.equal(i.has('zzz'), false);
});

test('locale regional cai no idioma base', () => {
  const i = createI18n({ locale: 'en-US', messages });
  assert.equal(i.t('hello'), 'Hello');
});
