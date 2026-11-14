import { test } from 'node:test';
import assert from 'node:assert/strict';
import { hexParaRgb, rgbParaHex, rgbParaHsl, hslParaRgb, hexParaHsl, hslParaHex } from './cor.js';

test('hex <-> rgb', () => {
  assert.deepEqual(hexParaRgb('#ff8000'), { r: 255, g: 128, b: 0 });
  assert.deepEqual(hexParaRgb('#0f0'), { r: 0, g: 255, b: 0 });
  assert.equal(rgbParaHex({ r: 255, g: 128, b: 0 }), '#ff8000');
  assert.throws(() => hexParaRgb('#zzz'), TypeError);
});
test('rgb -> hsl', () => {
  assert.deepEqual(rgbParaHsl({ r: 255, g: 0, b: 0 }), { h: 0, s: 100, l: 50 });
  assert.deepEqual(rgbParaHsl({ r: 0, g: 0, b: 255 }), { h: 240, s: 100, l: 50 });
  assert.deepEqual(rgbParaHsl({ r: 128, g: 128, b: 128 }), { h: 0, s: 0, l: 50 });
});
test('hsl -> rgb', () => {
  assert.deepEqual(hslParaRgb({ h: 120, s: 100, l: 50 }), { r: 0, g: 255, b: 0 });
  assert.deepEqual(hslParaRgb({ h: 0, s: 0, l: 100 }), { r: 255, g: 255, b: 255 });
});
test('atalhos e ida e volta', () => {
  assert.deepEqual(hexParaHsl('#ffff00'), { h: 60, s: 100, l: 50 });
  assert.equal(hslParaHex({ h: 240, s: 100, l: 50 }), '#0000ff');
  assert.equal(hslParaHex(hexParaHsl('#ff0000')), '#ff0000');
});
