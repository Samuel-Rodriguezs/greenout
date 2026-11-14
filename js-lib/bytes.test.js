import { test } from 'node:test';
import assert from 'node:assert/strict';
import { formatarBytes, parseBytes } from './bytes.js';

test('formatar binário', () => {
  assert.equal(formatarBytes(0), '0 B');
  assert.equal(formatarBytes(1023), '1023 B');
  assert.equal(formatarBytes(1024), '1 KiB');
  assert.equal(formatarBytes(1536), '1.5 KiB');
  assert.equal(formatarBytes(1048576 * 3.25), '3.25 MiB');
});
test('formatar decimal e casas', () => {
  assert.equal(formatarBytes(1500, { base: 1000 }), '1.5 kB');
  assert.equal(formatarBytes(1234567, { casas: 1, base: 1000 }), '1.2 MB');
});
test('formatar inválido', () => assert.throws(() => formatarBytes(-1), RangeError));
test('parse', () => {
  assert.equal(parseBytes('1.5 KiB'), 1536);
  assert.equal(parseBytes('2kB'), 2000);
  assert.equal(parseBytes('42'), 42);
  assert.throws(() => parseBytes('abc'), SyntaxError);
});
