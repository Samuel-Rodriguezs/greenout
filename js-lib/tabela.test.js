import { test } from 'node:test';
import assert from 'node:assert/strict';
import { tabela } from './tabela.js';

test('renderiza tabela alinhada', () => {
  const t = tabela(['Nome', 'Idade'], [['Ana', 30], ['Bartolomeu', 7]]);
  assert.equal(t, [
    '+------------+-------+',
    '| Nome       | Idade |',
    '+------------+-------+',
    '| Ana        |    30 |',
    '| Bartolomeu |     7 |',
    '+------------+-------+',
  ].join('\n'));
});
test('sem linhas e células ausentes', () => {
  assert.equal(tabela(['A'], []), '+---+\n| A |\n+---+\n+---+');
  assert.match(tabela(['A', 'B'], [['x']]), /\| x \|   \|/);
});
