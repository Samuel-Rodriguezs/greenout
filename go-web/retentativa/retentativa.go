// Pacote retentativa fornece um http.RoundTripper que repete requisições com
// backoff exponencial em erros de rede e respostas 5xx/429.
package retentativa

import (
	"io"
	"net/http"
	"strconv"
	"time"
)

// Transporte envolve outro RoundTripper adicionando retentativas.
type Transporte struct {
	Base          http.RoundTripper   // padrão: http.DefaultTransport
	MaxTentativas int                 // total de tentativas (padrão 3)
	EsperaInicial time.Duration       // padrão 100ms; dobra a cada tentativa
	EsperaMaxima  time.Duration       // teto do backoff (0 = sem teto)
	Dormir        func(time.Duration) // injetável; padrão time.Sleep
}

func (t *Transporte) deveRepetir(resp *http.Response, err error) bool {
	if err != nil {
		return true
	}
	return resp.StatusCode == http.StatusTooManyRequests || resp.StatusCode >= 500
}

func (t *Transporte) espera(tentativa int, resp *http.Response) time.Duration {
	if resp != nil {
		if s, err := strconv.Atoi(resp.Header.Get("Retry-After")); err == nil && s >= 0 {
			return time.Duration(s) * time.Second
		}
	}
	ini := t.EsperaInicial
	if ini == 0 {
		ini = 100 * time.Millisecond
	}
	d := ini << (tentativa - 1)
	if t.EsperaMaxima > 0 && d > t.EsperaMaxima {
		d = t.EsperaMaxima
	}
	return d
}

// RoundTrip implementa http.RoundTripper. Métodos com corpo só são repetidos
// se o corpo puder ser relido (GetBody).
func (t *Transporte) RoundTrip(req *http.Request) (*http.Response, error) {
	base := t.Base
	if base == nil {
		base = http.DefaultTransport
	}
	max := t.MaxTentativas
	if max <= 0 {
		max = 3
	}
	dormir := t.Dormir
	if dormir == nil {
		dormir = time.Sleep
	}
	for tent := 1; ; tent++ {
		r := req
		if tent > 1 && req.Body != nil && req.Body != http.NoBody {
			if req.GetBody == nil {
				return nil, io.ErrUnexpectedEOF
			}
			corpo, err := req.GetBody()
			if err != nil {
				return nil, err
			}
			r = req.Clone(req.Context())
			r.Body = corpo
		}
		resp, err := base.RoundTrip(r)
		repetivel := req.Body == nil || req.Body == http.NoBody || req.GetBody != nil
		if !t.deveRepetir(resp, err) || tent >= max || !repetivel {
			return resp, err
		}
		espera := t.espera(tent, resp)
		if resp != nil {
			io.Copy(io.Discard, resp.Body)
			resp.Body.Close()
		}
		select {
		case <-req.Context().Done():
			return nil, req.Context().Err()
		default:
		}
		dormir(espera)
	}
}
