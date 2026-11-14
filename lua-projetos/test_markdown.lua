local md = require("markdown")
local c = md.converter
assert(c("") == "")
assert(c("\n\n  \n") == "")
assert(c("# Título") == "<h1>Título</h1>")
assert(c("###### Seis") == "<h6>Seis</h6>")
assert(c("####### Sete") == "<p>####### Sete</p>")      -- mais de 6 não é título
assert(c("#sem espaço") == "<p>#sem espaço</p>")
assert(c("Olá mundo") == "<p>Olá mundo</p>")
assert(c("linha 1\nlinha 2") == "<p>linha 1 linha 2</p>")
assert(c("a\n\nb") == "<p>a</p>\n<p>b</p>")
assert(c("**forte** e *suave*") == "<p><strong>forte</strong> e <em>suave</em></p>")
assert(c("use `x < y` aqui") == "<p>use <code>x &lt; y</code> aqui</p>")
assert(c("`*não itálico*`") == "<p><code>*não itálico*</code></p>")
assert(c("[site](http://a.com)") == '<p><a href="http://a.com">site</a></p>')
assert(c("a & b <c>") == "<p>a &amp; b &lt;c&gt;</p>")
assert(c("- um\n- dois") == "<ul><li>um</li><li>dois</li></ul>")
assert(c("* um\n* **dois**") == "<ul><li>um</li><li><strong>dois</strong></li></ul>")
assert(c("1. a\n2. b") == "<ol><li>a</li><li>b</li></ol>")
assert(c("> citado\n> de novo") == "<blockquote>citado de novo</blockquote>")
assert(c("```\nlocal x = 1 < 2\n```") == "<pre><code>local x = 1 &lt; 2</code></pre>")
assert(c("```\nsem fechar") == "<pre><code>sem fechar</code></pre>")
assert(c("```\n# não é título\n```") == "<pre><code># não é título</code></pre>")
-- documento misto
local doc = "# T\n\ntexto *i*\n\n- a\n- b\n\n1. x\n\n> q\n\nfim"
assert(c(doc) == "<h1>T</h1>\n<p>texto <em>i</em></p>\n<ul><li>a</li><li>b</li></ul>\n<ol><li>x</li></ol>\n<blockquote>q</blockquote>\n<p>fim</p>")
-- parágrafo interrompido por lista
assert(c("texto\n- item") == "<p>texto</p>\n<ul><li>item</li></ul>")
-- CRLF
assert(c("# a\r\n\r\nb") == "<h1>a</h1>\n<p>b</p>")
print("ok")
