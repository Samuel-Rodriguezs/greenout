package disjuntor

import (
	"errors"
	"io"
	"net/http"
	"strings"
	"testing"
	"time"
)

type falso struct {
	status   int
	err      error
	chamadas int
}

func (f *falso) RoundTrip(*http.Request) (*http.Response, error) {
	f.chamadas++
	if f.err != nil {
		return nil, f.err
	}
	return &http.Response{StatusCode: f.status, Body: io.NopCloser(strings.NewReader(""))}, nil
}

func TestCicloCompleto(t *testing.T) {
	agora := time.Unix(0, 0)
	f := &falso{status: 500}
	d := Novo(f, 3, 10*time.Second, func() time.Time { return agora })
	req, _ := http.NewRequest("GET", "http://exemplo.test/", nil)

	passos := []struct {
		nome        string
		avanca      time.Duration
		status      int // status do falso antes da chamada
		erro        error
		estadoApos  Estado
		chamadasTot int
	}{
		{"falha 1", 0, 500, nil, Fechado, 1},
		{"falha 2", 0, 500, nil, Fechado, 2},
		{"falha 3 abre", 0, 500, nil, Aberto, 3},
		{"rejeita aberto", 5 * time.Second, 200, ErrAberto, Aberto, 3},
		{"sonda falha reabre", 5 * time.Second, 500, nil, Aberto, 4},
		{"rejeita de novo", 9 * time.Second, 200, ErrAberto, Aberto, 4},
		{"sonda ok fecha", 1 * time.Second, 200, nil, Fechado, 5},
		{"fechado funciona", 0, 200, nil, Fechado, 6},
	}
	for _, p := range passos {
		t.Run(p.nome, func(t *testing.T) {
			agora = agora.Add(p.avanca)
			f.status = p.status
			resp, err := d.RoundTrip(req)
			if !errors.Is(err, p.erro) {
				t.Fatalf("erro %v, esperado %v", err, p.erro)
			}
			if err == nil {
				resp.Body.Close()
			}
			if got := d.Estado(); got != p.estadoApos {
				t.Errorf("estado %v, esperado %v", got, p.estadoApos)
			}
			if f.chamadas != p.chamadasTot {
				t.Errorf("chamadas %d, esperado %d", f.chamadas, p.chamadasTot)
			}
		})
	}
}

func TestSucessoZeraFalhas(t *testing.T) {
	f := &falso{}
	d := Novo(f, 2, time.Minute, func() time.Time { return time.Unix(0, 0) })
	req, _ := http.NewRequest("GET", "http://exemplo.test/", nil)
	for _, st := range []int{500, 200, 500, 200} {
		f.status = st
		d.RoundTrip(req)
	}
	if d.Estado() != Fechado {
		t.Errorf("falhas não consecutivas não deveriam abrir; estado %v", d.Estado())
	}
}

func TestErroDeRedeConta(t *testing.T) {
	f := &falso{err: errors.New("timeout")}
	d := Novo(f, 2, time.Minute, func() time.Time { return time.Unix(0, 0) })
	req, _ := http.NewRequest("GET", "http://exemplo.test/", nil)
	d.RoundTrip(req)
	d.RoundTrip(req)
	if _, err := d.RoundTrip(req); !errors.Is(err, ErrAberto) {
		t.Errorf("esperado ErrAberto, obtido %v", err)
	}
}

func TestEstadoString(t *testing.T) {
	if Aberto.String() != "aberto" || MeioAberto.String() != "meio-aberto" || Fechado.String() != "fechado" {
		t.Error("String() incorreto")
	}
}
