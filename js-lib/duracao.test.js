import { test } from 'node:test';
import assert from 'node:assert/strict';
import { parseDuracao, formatarDuracao } from './duracao.js';

test('parse', () => {
  assert.equal(parseDuracao('1h30m'), 5400000);
  assert.equal(parseDuracao('2d 4h'), 2 * 86400000 + 4 * 3600000);
  assert.equal(parseDuracao('500ms'), 500);
  assert.equal(parseDuracao('1.5h'), 5400000);
});
test('parse inválido', () => {
  for (const x of ['', 'abc', '10', '1h xx', 'x1h']) assert.throws(() => parseDuracao(x), SyntaxError, x);
});
test('formatar', () => {
  assert.equal(formatarDuracao(5400000), '1h30m');
  assert.equal(formatarDuracao(90061001), '1d1h1m1s1ms');
  assert.equal(formatarDuracao(0), '0s');
  assert.equal(formatarDuracao(-1000), '-1s');
});
test('ida e volta', () => assert.equal(formatarDuracao(parseDuracao('3h5m10s')), '3h5m10s'));
