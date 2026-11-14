// Pacote encurtador implementa uma API completa de URL shortener:
//
//	POST   /api/links          cria {"url": "...", "codigo": "opcional"}
//	GET    /api/links/{codigo} estatísticas
//	DELETE /api/links/{codigo} remove
//	GET    /{codigo}           redireciona (302) e conta o acesso
package encurtador

import (
	"crypto/rand"
	"encoding/json"
	"errors"
	"net/http"
	"net/url"
	"regexp"
	"sync"
	"time"
)

// Link é uma URL encurtada.
type Link struct {
	Codigo   string    `json:"codigo"`
	URL      string    `json:"url"`
	Acessos  int       `json:"acessos"`
	CriadoEm time.Time `json:"criado_em"`
}

// Erros do serviço.
var (
	ErrNaoEncontrado  = errors.New("link não encontrado")
	ErrCodigoEmUso    = errors.New("código já em uso")
	ErrURLInvalida    = errors.New("url inválida: use http ou https com host")
	ErrCodigoInvalido = errors.New("código inválido: use 3 a 32 letras, números, '-' ou '_'")
)

var reCodigo = regexp.MustCompile(`^[A-Za-z0-9_-]{3,32}$`)

// Servico guarda os links em memória.
type Servico struct {
	Agora func() time.Time
	Gerar func() string // gerador de códigos (injetável)
	mu    sync.Mutex
	links map[string]*Link
}

const alfabeto = "abcdefghijkmnopqrstuvwxyzABCDEFGHJKLMNPQRSTUVWXYZ23456789"

func gerarAleatorio() string {
	b := make([]byte, 7)
	rand.Read(b)
	for i := range b {
		b[i] = alfabeto[int(b[i])%len(alfabeto)]
	}
	return string(b)
}

// Novo cria um serviço. Parâmetros nulos usam time.Now e gerador aleatório.
func Novo(agora func() time.Time, gerar func() string) *Servico {
	if agora == nil {
		agora = time.Now
	}
	if gerar == nil {
		gerar = gerarAleatorio
	}
	return &Servico{Agora: agora, Gerar: gerar, links: map[string]*Link{}}
}

// Criar valida e registra o link; codigo vazio gera um automaticamente.
func (s *Servico) Criar(alvo, codigo string) (Link, error) {
	u, err := url.Parse(alvo)
	if err != nil || (u.Scheme != "http" && u.Scheme != "https") || u.Host == "" {
		return Link{}, ErrURLInvalida
	}
	if codigo != "" && !reCodigo.MatchString(codigo) {
		return Link{}, ErrCodigoInvalido
	}
	s.mu.Lock()
	defer s.mu.Unlock()
	if codigo == "" {
		for {
			codigo = s.Gerar()
			if _, existe := s.links[codigo]; !existe {
				break
			}
		}
	} else if _, existe := s.links[codigo]; existe {
		return Link{}, ErrCodigoEmUso
	}
	l := &Link{Codigo: codigo, URL: alvo, CriadoEm: s.Agora()}
	s.links[codigo] = l
	return *l, nil
}

// Resolver devolve a URL de destino e incrementa o contador.
func (s *Servico) Resolver(codigo string) (string, error) {
	s.mu.Lock()
	defer s.mu.Unlock()
	l, ok := s.links[codigo]
	if !ok {
		return "", ErrNaoEncontrado
	}
	l.Acessos++
	return l.URL, nil
}

// Obter devolve o link com estatísticas, sem contar acesso.
func (s *Servico) Obter(codigo string) (Link, error) {
	s.mu.Lock()
	defer s.mu.Unlock()
	l, ok := s.links[codigo]
	if !ok {
		return Link{}, ErrNaoEncontrado
	}
	return *l, nil
}

// Remover apaga o link.
func (s *Servico) Remover(codigo string) error {
	s.mu.Lock()
	defer s.mu.Unlock()
	if _, ok := s.links[codigo]; !ok {
		return ErrNaoEncontrado
	}
	delete(s.links, codigo)
	return nil
}

// Handler expõe o serviço via HTTP.
func (s *Servico) Handler() http.Handler {
	m := http.NewServeMux()
	m.HandleFunc("POST /api/links", s.criar)
	m.HandleFunc("GET /api/links/{codigo}", s.stats)
	m.HandleFunc("DELETE /api/links/{codigo}", s.remover)
	m.HandleFunc("GET /{codigo}", s.redirecionar)
	return m
}

func resposta(w http.ResponseWriter, status int, v any) {
	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(status)
	json.NewEncoder(w).Encode(v)
}

func statusDe(err error) int {
	switch {
	case errors.Is(err, ErrNaoEncontrado):
		return http.StatusNotFound
	case errors.Is(err, ErrCodigoEmUso):
		return http.StatusConflict
	default:
		return http.StatusBadRequest
	}
}

func (s *Servico) criar(w http.ResponseWriter, r *http.Request) {
	var req struct {
		URL    string `json:"url"`
		Codigo string `json:"codigo"`
	}
	if err := json.NewDecoder(http.MaxBytesReader(w, r.Body, 1<<16)).Decode(&req); err != nil {
		resposta(w, http.StatusBadRequest, map[string]string{"erro": "JSON inválido"})
		return
	}
	l, err := s.Criar(req.URL, req.Codigo)
	if err != nil {
		resposta(w, statusDe(err), map[string]string{"erro": err.Error()})
		return
	}
	w.Header().Set("Location", "/"+l.Codigo)
	resposta(w, http.StatusCreated, l)
}

func (s *Servico) stats(w http.ResponseWriter, r *http.Request) {
	l, err := s.Obter(r.PathValue("codigo"))
	if err != nil {
		resposta(w, statusDe(err), map[string]string{"erro": err.Error()})
		return
	}
	resposta(w, http.StatusOK, l)
}

func (s *Servico) remover(w http.ResponseWriter, r *http.Request) {
	if err := s.Remover(r.PathValue("codigo")); err != nil {
		resposta(w, statusDe(err), map[string]string{"erro": err.Error()})
		return
	}
	w.WriteHeader(http.StatusNoContent)
}

func (s *Servico) redirecionar(w http.ResponseWriter, r *http.Request) {
	alvo, err := s.Resolver(r.PathValue("codigo"))
	if err != nil {
		resposta(w, statusDe(err), map[string]string{"erro": err.Error()})
		return
	}
	http.Redirect(w, r, alvo, http.StatusFound)
}
