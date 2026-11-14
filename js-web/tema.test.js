import test from 'node:test';
import assert from 'node:assert/strict';
import {
  hexParaRgb, rgbParaHex, luminancia, contraste, nivelWCAG, corLegivel,
  misturar, ajustarParaContraste, createTemaManager,
} from './tema.js';

test('conversões hex/rgb', () => {
  assert.deepEqual(hexParaRgb('#fff'), [255, 255, 255]);
  assert.deepEqual(hexParaRgb('1a2B3c'), [26, 43, 60]);
  assert.equal(rgbParaHex([26, 43, 60]), '#1a2b3c');
  assert.throws(() => hexParaRgb('#12'));
});

test('luminância e contraste de referência', () => {
  assert.equal(luminancia('#000000'), 0);
  assert.equal(luminancia('#ffffff'), 1);
  assert.equal(contraste('#000', '#fff'), 21);
  assert.equal(contraste('#fff', '#fff'), 1);
  assert.ok(Math.abs(contraste('#777777', '#ffffff') - 4.48) < 0.02);
});

test('níveis WCAG', () => {
  assert.equal(nivelWCAG('#000', '#fff'), 'AAA');
  assert.equal(nivelWCAG('#767676', '#fff'), 'AA');
  assert.equal(nivelWCAG('#777', '#fff'), 'falha');
  assert.equal(nivelWCAG('#777', '#fff', { grande: true }), 'AA');
});

test('cor legível', () => {
  assert.equal(corLegivel('#000033'), '#ffffff');
  assert.equal(corLegivel('#ffee99'), '#000000');
});

test('misturar', () => {
  assert.equal(misturar('#000000', '#ffffff', 0.5), '#808080');
});

test('ajustar para contraste mínimo', () => {
  const novo = ajustarParaContraste('#aaaaaa', '#ffffff', 4.5);
  assert.ok(contraste(novo, '#ffffff') >= 4.5);
  assert.equal(ajustarParaContraste('#000', '#fff'), '#000');
});

test('gerenciador de temas', () => {
  const mudancas = [];
  const m = createTemaManager({
    temas: {
      claro: { texto: '#111111', fundo: '#ffffff' },
      escuro: { texto: '#eeeeee', fundo: '#111111' },
    },
    inicial: 'claro',
    onChange: (n) => mudancas.push(n),
  });
  assert.equal(m.atual, 'claro');
  m.alternar();
  assert.equal(m.atual, 'escuro');
  m.seguirSistema(false);
  assert.deepEqual(mudancas, ['escuro', 'claro']);
  assert.equal(m.auditar()[0].nivel, 'AAA');
  assert.throws(() => m.definir('x'));
});
