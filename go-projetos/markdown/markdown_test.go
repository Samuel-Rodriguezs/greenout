package markdown

import "testing"

func TestConverter(t *testing.T) {
	casos := []struct {
		nome, entrada, want string
	}{
		{"vazio", "", ""},
		{"titulo 1", "# Olá", "<h1>Olá</h1>"},
		{"titulo 3", "### Sub", "<h3>Sub</h3>"},
		{"sem espaço não é título", "#Olá", "<p>#Olá</p>"},
		{"paragrafo", "uma\nlinha\n\noutra", "<p>uma linha</p>\n<p>outra</p>"},
		{"negrito e italico", "**forte** e *leve*", "<p><strong>forte</strong> e <em>leve</em></p>"},
		{"codigo", "use `go test`", "<p>use <code>go test</code></p>"},
		{"lista", "- a\n- b", "<ul>\n<li>a</li>\n<li>b</li>\n</ul>"},
		{"escape html", "<script>", "<p>&lt;script&gt;</p>"},
		{"misto", "# T\ntexto\n- x\n\nfim", "<h1>T</h1>\n<p>texto</p>\n<ul>\n<li>x</li>\n</ul>\n<p>fim</p>"},
		{"crlf", "# A\r\n\r\nb", "<h1>A</h1>\n<p>b</p>"},
		{"lista depois de paragrafo fecha lista", "- a\ntexto", "<ul>\n<li>a</li>\n</ul>\n<p>texto</p>"},
	}
	for _, c := range casos {
		t.Run(c.nome, func(t *testing.T) {
			if got := Converter(c.entrada); got != c.want {
				t.Errorf("got:\n%q\nwant:\n%q", got, c.want)
			}
		})
	}
}
