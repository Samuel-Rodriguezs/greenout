import { test } from 'node:test';
import assert from 'node:assert/strict';
import { escaparHtml, desescaparHtml, removerTags, sanitizarHtml } from './sanitizar.js';

test('escapar e desescapar', () => {
  const s = `<a href="x">Tom & 'Jerry'</a>`;
  assert.equal(escaparHtml(s), '&lt;a href=&quot;x&quot;&gt;Tom &amp; &#39;Jerry&#39;&lt;/a&gt;');
  assert.equal(desescaparHtml(escaparHtml(s)), s);
});
test('desescapar não faz duplo decode', () => assert.equal(desescaparHtml('&amp;lt;'), '&lt;'));
test('removerTags tira scripts e comentários', () => {
  assert.equal(removerTags('<p>Oi <b>mundo</b><script>alert(1)</script><!-- c --></p>'), 'Oi mundo');
});
test('sanitizarHtml', () => {
  assert.equal(sanitizarHtml('<img src=x onerror=alert(1)>a < b'), 'a &lt; b');
});
