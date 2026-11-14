package smtp

import (
	"errors"
	"reflect"
	"strings"
	"testing"
)

func TestParseComando(t *testing.T) {
	casos := []struct {
		linha string
		want  Comando
		erro  error
	}{
		{"HELO cliente.exemplo", Comando{"HELO", "cliente.exemplo", ""}, nil},
		{"ehlo mail.exemplo.com", Comando{"EHLO", "mail.exemplo.com", ""}, nil},
		{"MAIL FROM:<ana@exemplo.com>", Comando{"MAIL", "FROM:<ana@exemplo.com>", "ana@exemplo.com"}, nil},
		{"mail from: <ana@exemplo.com> SIZE=100", Comando{"MAIL", "from: <ana@exemplo.com> SIZE=100", "ana@exemplo.com"}, nil},
		{"MAIL FROM:<>", Comando{"MAIL", "FROM:<>", ""}, nil},
		{"RCPT TO:<bob@exemplo.org>", Comando{"RCPT", "TO:<bob@exemplo.org>", "bob@exemplo.org"}, nil},
		{"DATA", Comando{"DATA", "", ""}, nil},
		{"quit", Comando{"QUIT", "", ""}, nil},
		{"RSET", Comando{"RSET", "", ""}, nil},
		{"NOOP qualquer coisa", Comando{"NOOP", "qualquer coisa", ""}, nil},
		{"VRFY ana", Comando{"VRFY", "ana", ""}, nil},

		{"", Comando{}, ErrDesconhecido},
		{"FOO bar", Comando{}, ErrDesconhecido},
		{"HELO", Comando{}, ErrSintaxe},
		{"HELO a b", Comando{}, ErrSintaxe},
		{"MAIL", Comando{}, ErrSintaxe},
		{"MAIL FROM ana@x.com", Comando{}, ErrSintaxe},
		{"MAIL FROM:ana@x.com", Comando{}, ErrSintaxe},
		{"MAIL FROM:<ana@x.com", Comando{}, ErrSintaxe},
		{"MAIL FROM:<ana>", Comando{}, ErrSintaxe},
		{"MAIL FROM:<@x.com>", Comando{}, ErrSintaxe},
		{"MAIL FROM:<ana@>", Comando{}, ErrSintaxe},
		{"MAIL FROM:<a b@x.com>", Comando{}, ErrSintaxe},
		{"MAIL FROM:<a@b@c>", Comando{}, ErrSintaxe},
		{"RCPT TO:<>", Comando{}, ErrSintaxe},
		{"RCPT FROM:<a@b.c>", Comando{}, ErrSintaxe},
		{"DATA agora", Comando{}, ErrSintaxe},
		{"VRFY", Comando{}, ErrSintaxe},
		{"HELO x\r\nQUIT", Comando{}, ErrSintaxe},
		{"HELO x\x00", Comando{}, ErrSintaxe},
		{"NOOP " + strings.Repeat("a", 600), Comando{}, ErrLinhaLonga},
	}
	for _, c := range casos {
		got, err := ParseComando(c.linha)
		if !errors.Is(err, c.erro) || (c.erro == nil && got != c.want) {
			t.Errorf("ParseComando(%.40q) = %+v, %v; esperava %+v, %v", c.linha, got, err, c.want, c.erro)
		}
	}
}

// roteiro executa pares (linha enviada, código esperado). Código 0 = sem resposta.
func roteiro(t *testing.T, s *Sessao, passos [][2]string) {
	t.Helper()
	for i, p := range passos {
		r, ok := s.Processar(p[0])
		want := p[1]
		switch {
		case want == "" && ok:
			t.Fatalf("passo %d (%q): esperava silêncio, veio %v", i, p[0], r)
		case want != "" && (!ok || r.String()[:3] != want):
			t.Fatalf("passo %d (%q): resposta %v (ok=%v), esperava %s", i, p[0], r, ok, want)
		}
	}
}

func TestSessaoCompleta(t *testing.T) {
	s := &Sessao{}
	if s.Saudacao().Codigo != 220 {
		t.Error("saudação")
	}
	roteiro(t, s, [][2]string{
		{"EHLO cli.exemplo", "250"},
		{"MAIL FROM:<ana@a.com>", "250"},
		{"RCPT TO:<bob@b.com>", "250"},
		{"RCPT TO:<cia@c.com>", "250"},
		{"DATA", "354"},
		{"Subject: oi", ""},
		{"", ""},
		{"..ponto no início", ""},
		{"fim", ""},
		{".", "250"},
		{"MAIL FROM:<dan@d.com>", "250"}, // pode iniciar nova transação
		{"RCPT TO:<eva@e.com>", "250"},
		{"RSET", "250"},
		{"RCPT TO:<eva@e.com>", "503"}, // RSET descartou o MAIL
		{"NOOP", "250"},
		{"VRFY ana", "252"},
		{"QUIT", "221"},
		{"NOOP", "421"},
	})
	want := []Mensagem{{
		De:    "ana@a.com",
		Para:  []string{"bob@b.com", "cia@c.com"},
		Corpo: "Subject: oi\n\n.ponto no início\nfim",
	}}
	if !reflect.DeepEqual(s.Mensagens(), want) {
		t.Errorf("mensagens = %+v", s.Mensagens())
	}
	if !s.Fechada {
		t.Error("sessão deveria estar fechada")
	}
}

func TestSessaoOrdemInvalida(t *testing.T) {
	roteiro(t, &Sessao{}, [][2]string{
		{"MAIL FROM:<a@b.c>", "503"},
		{"RCPT TO:<a@b.c>", "503"},
		{"DATA", "503"},
		{"HELO x", "250"},
		{"RCPT TO:<a@b.c>", "503"},
		{"DATA", "503"},
		{"MAIL FROM:<a@b.c>", "250"},
		{"MAIL FROM:<d@e.f>", "503"},
		{"DATA", "503"}, // sem destinatário
		{"RCPT TO:<x@y.z>", "250"},
		{"DATA", "354"},
	})
}

func TestSessaoErros(t *testing.T) {
	roteiro(t, &Sessao{}, [][2]string{
		{"XYZZY", "500"},
		{"", "500"},
		{"HELO", "501"},
		{"HELO a", "250"},
		{"MAIL FROM:ana", "501"},
		{strings.Repeat("A", 600), "500"},
	})
}

func TestSessaoRemetenteNulo(t *testing.T) {
	s := &Sessao{}
	roteiro(t, s, [][2]string{
		{"HELO x", "250"}, {"MAIL FROM:<>", "250"}, {"RCPT TO:<a@b.c>", "250"},
		{"DATA", "354"}, {"bounce", ""}, {".", "250"},
	})
	if m := s.Mensagens(); len(m) != 1 || m[0].De != "" || m[0].Corpo != "bounce" {
		t.Errorf("mensagens = %+v", m)
	}
}

func TestNovoHeloReiniciaTransacao(t *testing.T) {
	s := &Sessao{}
	roteiro(t, s, [][2]string{
		{"HELO a", "250"}, {"MAIL FROM:<a@b.c>", "250"}, {"HELO b", "250"}, {"RCPT TO:<x@y.z>", "503"},
	})
}
