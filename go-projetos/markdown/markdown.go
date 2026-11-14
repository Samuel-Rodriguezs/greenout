// Pacote markdown converte um subconjunto simples de Markdown em HTML:
// títulos (#), parágrafos, listas (-), negrito, itálico e código inline.
package markdown

import (
	"html"
	"regexp"
	"strings"
)

var (
	reNegrito = regexp.MustCompile(`\*\*(.+?)\*\*`)
	reItalico = regexp.MustCompile(`\*(.+?)\*`)
	reCodigo  = regexp.MustCompile("`([^`]+)`")
	reTitulo  = regexp.MustCompile(`^(#{1,6})\s+(.*)$`)
)

// inline aplica formatação dentro de uma linha, escapando o HTML antes.
func inline(s string) string {
	s = html.EscapeString(s)
	s = reCodigo.ReplaceAllString(s, "<code>$1</code>")
	s = reNegrito.ReplaceAllString(s, "<strong>$1</strong>")
	s = reItalico.ReplaceAllString(s, "<em>$1</em>")
	return s
}

// Converter transforma o texto Markdown em HTML.
func Converter(texto string) string {
	var saida []string
	var paragrafo []string
	emLista := false

	fecharParagrafo := func() {
		if len(paragrafo) > 0 {
			saida = append(saida, "<p>"+inline(strings.Join(paragrafo, " "))+"</p>")
			paragrafo = nil
		}
	}
	fecharLista := func() {
		if emLista {
			saida = append(saida, "</ul>")
			emLista = false
		}
	}

	for _, linha := range strings.Split(strings.ReplaceAll(texto, "\r\n", "\n"), "\n") {
		linha = strings.TrimSpace(linha)
		switch {
		case linha == "":
			fecharParagrafo()
			fecharLista()
		case reTitulo.MatchString(linha):
			fecharParagrafo()
			fecharLista()
			m := reTitulo.FindStringSubmatch(linha)
			n := len(m[1])
			saida = append(saida, "<h"+string(rune('0'+n))+">"+inline(m[2])+"</h"+string(rune('0'+n))+">")
		case strings.HasPrefix(linha, "- "):
			fecharParagrafo()
			if !emLista {
				saida = append(saida, "<ul>")
				emLista = true
			}
			saida = append(saida, "<li>"+inline(strings.TrimPrefix(linha, "- "))+"</li>")
		default:
			fecharLista()
			paragrafo = append(paragrafo, linha)
		}
	}
	fecharParagrafo()
	fecharLista()
	return strings.Join(saida, "\n")
}
