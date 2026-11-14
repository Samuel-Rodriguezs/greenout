package negociacao

import "testing"

func TestEscolher(t *testing.T) {
	ofertas := []string{"application/json", "text/html", "text/plain"}
	casos := []struct {
		nome, accept, esperado string
	}{
		{"vazio usa primeira", "", "application/json"},
		{"exato", "text/html", "text/html"},
		{"curinga", "*/*", "application/json"},
		{"tipo curinga", "text/*", "text/html"},
		{"q decide", "text/html;q=0.5, application/json;q=0.9", "application/json"},
		{"q zero exclui", "application/json;q=0, text/plain", "text/plain"},
		{"específico vence curinga", "*/*;q=0.1, text/plain", "text/plain"},
		{"nada aceitável", "image/png", ""},
		{"maiúsculas", "TEXT/HTML", "text/html"},
		{"lixo ignorado", "xyz, text/plain", "text/plain"},
	}
	for _, c := range casos {
		t.Run(c.nome, func(t *testing.T) {
			if got := Escolher(c.accept, ofertas); got != c.esperado {
				t.Errorf("Escolher(%q) = %q, esperado %q", c.accept, got, c.esperado)
			}
		})
	}
	if Escolher("*/*", nil) != "" {
		t.Error("sem ofertas deveria retornar vazio")
	}
}
