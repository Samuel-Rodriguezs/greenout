package retentativa

import (
	"errors"
	"io"
	"net/http"
	"reflect"
	"strings"
	"testing"
	"time"
)

type resultado struct {
	status int
	err    error
	header http.Header
}

// falso devolve resultados em sequência e registra corpos recebidos.
type falso struct {
	resultados []resultado
	chamadas   int
	corpos     []string
}

func (f *falso) RoundTrip(r *http.Request) (*http.Response, error) {
	if r.Body != nil {
		b, _ := io.ReadAll(r.Body)
		f.corpos = append(f.corpos, string(b))
	}
	res := f.resultados[min(f.chamadas, len(f.resultados)-1)]
	f.chamadas++
	if res.err != nil {
		return nil, res.err
	}
	h := res.header
	if h == nil {
		h = http.Header{}
	}
	return &http.Response{StatusCode: res.status, Header: h, Body: io.NopCloser(strings.NewReader("x"))}, nil
}

func TestRoundTrip(t *testing.T) {
	erroRede := errors.New("conexão recusada")
	casos := []struct {
		nome       string
		resultados []resultado
		max        int
		status     int
		erro       error
		chamadas   int
		esperas    []time.Duration
	}{
		{"sucesso direto", []resultado{{status: 200}}, 3, 200, nil, 1, nil},
		{"500 depois 200", []resultado{{status: 500}, {status: 200}}, 3, 200, nil, 2, []time.Duration{100 * time.Millisecond}},
		{"backoff dobra", []resultado{{status: 503}, {status: 503}, {status: 200}}, 4, 200, nil, 3, []time.Duration{100 * time.Millisecond, 200 * time.Millisecond}},
		{"esgota tentativas", []resultado{{status: 500}}, 3, 500, nil, 3, []time.Duration{100 * time.Millisecond, 200 * time.Millisecond}},
		{"erro de rede", []resultado{{err: erroRede}, {status: 200}}, 3, 200, nil, 2, []time.Duration{100 * time.Millisecond}},
		{"erro persistente", []resultado{{err: erroRede}}, 2, 0, erroRede, 2, []time.Duration{100 * time.Millisecond}},
		{"400 não repete", []resultado{{status: 400}}, 3, 400, nil, 1, nil},
		{"429 respeita Retry-After", []resultado{{status: 429, header: http.Header{"Retry-After": {"2"}}}, {status: 200}}, 3, 200, nil, 2, []time.Duration{2 * time.Second}},
	}
	for _, c := range casos {
		t.Run(c.nome, func(t *testing.T) {
			f := &falso{resultados: c.resultados}
			var esperas []time.Duration
			tr := &Transporte{Base: f, MaxTentativas: c.max, Dormir: func(d time.Duration) { esperas = append(esperas, d) }}
			req, _ := http.NewRequest("GET", "http://exemplo.test/", nil)
			resp, err := tr.RoundTrip(req)
			if !errors.Is(err, c.erro) {
				t.Fatalf("erro %v, esperado %v", err, c.erro)
			}
			if err == nil && resp.StatusCode != c.status {
				t.Errorf("status %d, esperado %d", resp.StatusCode, c.status)
			}
			if f.chamadas != c.chamadas {
				t.Errorf("chamadas %d, esperado %d", f.chamadas, c.chamadas)
			}
			if !reflect.DeepEqual(esperas, c.esperas) {
				t.Errorf("esperas %v, esperado %v", esperas, c.esperas)
			}
		})
	}
}

func TestCorpoReenviado(t *testing.T) {
	f := &falso{resultados: []resultado{{status: 502}, {status: 201}}}
	tr := &Transporte{Base: f, Dormir: func(time.Duration) {}}
	req, _ := http.NewRequest("POST", "http://exemplo.test/", strings.NewReader("dados"))
	resp, err := tr.RoundTrip(req)
	if err != nil || resp.StatusCode != 201 {
		t.Fatalf("resp=%v err=%v", resp, err)
	}
	if !reflect.DeepEqual(f.corpos, []string{"dados", "dados"}) {
		t.Errorf("corpos %v", f.corpos)
	}
}

func TestCorpoNaoRepetivel(t *testing.T) {
	f := &falso{resultados: []resultado{{status: 500}, {status: 200}}}
	tr := &Transporte{Base: f, Dormir: func(time.Duration) {}}
	req, _ := http.NewRequest("POST", "http://exemplo.test/", io.NopCloser(strings.NewReader("x")))
	resp, _ := tr.RoundTrip(req)
	if f.chamadas != 1 || resp.StatusCode != 500 {
		t.Errorf("chamadas=%d status=%d; corpo sem GetBody não deve ser repetido", f.chamadas, resp.StatusCode)
	}
}

func TestTetoDoBackoff(t *testing.T) {
	f := &falso{resultados: []resultado{{status: 500}}}
	var esperas []time.Duration
	tr := &Transporte{Base: f, MaxTentativas: 5, EsperaInicial: time.Second, EsperaMaxima: 3 * time.Second,
		Dormir: func(d time.Duration) { esperas = append(esperas, d) }}
	req, _ := http.NewRequest("GET", "http://exemplo.test/", nil)
	tr.RoundTrip(req)
	esperado := []time.Duration{time.Second, 2 * time.Second, 3 * time.Second, 3 * time.Second}
	if !reflect.DeepEqual(esperas, esperado) {
		t.Errorf("esperas %v, esperado %v", esperas, esperado)
	}
}

func TestUsadoPorCliente(t *testing.T) {
	f := &falso{resultados: []resultado{{status: 500}, {status: 200}}}
	c := &http.Client{Transport: &Transporte{Base: f, Dormir: func(time.Duration) {}}}
	resp, err := c.Get("http://exemplo.test/")
	if err != nil || resp.StatusCode != 200 {
		t.Fatalf("resp=%v err=%v", resp, err)
	}
}
