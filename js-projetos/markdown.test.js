import test from 'node:test';
import assert from 'node:assert/strict';
import { markdownParaHtml, inline, escaparHtml } from './markdown.js';

test('títulos de níveis diferentes', () => {
  assert.equal(markdownParaHtml('# Olá\n### Três'), '<h1>Olá</h1>\n<h3>Três</h3>');
});

test('formatação inline', () => {
  assert.equal(
    inline('**negrito** e *itálico* e `cod`'),
    '<strong>negrito</strong> e <em>itálico</em> e <code>cod</code>',
  );
  assert.equal(inline('[site](http://x.com)'), '<a href="http://x.com">site</a>');
});

test('código inline não recebe formatação', () => {
  assert.equal(inline('`*a*`'), '<code>*a*</code>');
});

test('escapa HTML', () => {
  assert.equal(escaparHtml('<b>&"'), '&lt;b&gt;&amp;&quot;');
  assert.equal(markdownParaHtml('a <script> b'), '<p>a &lt;script&gt; b</p>');
});

test('listas ordenadas e não ordenadas', () => {
  assert.equal(markdownParaHtml('- a\n- b'), '<ul><li>a</li><li>b</li></ul>');
  assert.equal(markdownParaHtml('1. um\n2. dois'), '<ol><li>um</li><li>dois</li></ol>');
});

test('parágrafos juntam linhas e separam por linha em branco', () => {
  assert.equal(markdownParaHtml('a\nb\n\nc'), '<p>a b</p>\n<p>c</p>');
});

test('bloco de código preserva conteúdo', () => {
  assert.equal(markdownParaHtml('```\nif (a < b) {}\n```'), '<pre><code>if (a &lt; b) {}</code></pre>');
});

test('citação com conteúdo em markdown', () => {
  assert.equal(markdownParaHtml('> **oi**'), '<blockquote><p><strong>oi</strong></p></blockquote>');
});

test('bloco de código não fechado gera erro', () => {
  assert.throws(() => markdownParaHtml('```\nabc'), /não fechado/);
});
