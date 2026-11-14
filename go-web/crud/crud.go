// Pacote crud implementa uma API REST JSON de itens com store em memória protegido por mutex.
package crud

import (
	"encoding/json"
	"errors"
	"net/http"
	"sort"
	"strconv"
	"sync"
)

// Item é o recurso gerenciado.
type Item struct {
	ID    int     `json:"id"`
	Nome  string  `json:"nome"`
	Preco float64 `json:"preco"`
}

// ErrNaoEncontrado é retornado quando o ID não existe.
var ErrNaoEncontrado = errors.New("item não encontrado")

// Store guarda itens em memória.
type Store struct {
	mu    sync.RWMutex
	itens map[int]Item
	prox  int
}

// NovoStore cria um store vazio.
func NovoStore() *Store { return &Store{itens: map[int]Item{}, prox: 1} }

// Criar insere e atribui um ID.
func (s *Store) Criar(i Item) Item {
	s.mu.Lock()
	defer s.mu.Unlock()
	i.ID = s.prox
	s.prox++
	s.itens[i.ID] = i
	return i
}

// Obter busca por ID.
func (s *Store) Obter(id int) (Item, error) {
	s.mu.RLock()
	defer s.mu.RUnlock()
	i, ok := s.itens[id]
	if !ok {
		return Item{}, ErrNaoEncontrado
	}
	return i, nil
}

// Listar devolve todos ordenados por ID.
func (s *Store) Listar() []Item {
	s.mu.RLock()
	defer s.mu.RUnlock()
	res := make([]Item, 0, len(s.itens))
	for _, i := range s.itens {
		res = append(res, i)
	}
	sort.Slice(res, func(a, b int) bool { return res[a].ID < res[b].ID })
	return res
}

// Atualizar substitui um item existente.
func (s *Store) Atualizar(id int, i Item) (Item, error) {
	s.mu.Lock()
	defer s.mu.Unlock()
	if _, ok := s.itens[id]; !ok {
		return Item{}, ErrNaoEncontrado
	}
	i.ID = id
	s.itens[id] = i
	return i, nil
}

// Remover apaga um item.
func (s *Store) Remover(id int) error {
	s.mu.Lock()
	defer s.mu.Unlock()
	if _, ok := s.itens[id]; !ok {
		return ErrNaoEncontrado
	}
	delete(s.itens, id)
	return nil
}

// API expõe o store via HTTP.
type API struct{ Store *Store }

// Handler monta as rotas /itens e /itens/{id}.
func (a API) Handler() http.Handler {
	m := http.NewServeMux()
	m.HandleFunc("GET /itens", a.listar)
	m.HandleFunc("POST /itens", a.criar)
	m.HandleFunc("GET /itens/{id}", a.obter)
	m.HandleFunc("PUT /itens/{id}", a.atualizar)
	m.HandleFunc("DELETE /itens/{id}", a.remover)
	return m
}

func json_(w http.ResponseWriter, status int, v any) {
	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(status)
	if v != nil {
		json.NewEncoder(w).Encode(v)
	}
}

func erro(w http.ResponseWriter, status int, msg string) {
	json_(w, status, map[string]string{"erro": msg})
}

func lerItem(r *http.Request) (Item, error) {
	var i Item
	dec := json.NewDecoder(http.MaxBytesReader(nil, r.Body, 1<<20))
	dec.DisallowUnknownFields()
	if err := dec.Decode(&i); err != nil {
		return i, errors.New("JSON inválido")
	}
	if i.Nome == "" {
		return i, errors.New("nome é obrigatório")
	}
	if i.Preco < 0 {
		return i, errors.New("preço não pode ser negativo")
	}
	return i, nil
}

func idDe(w http.ResponseWriter, r *http.Request) (int, bool) {
	id, err := strconv.Atoi(r.PathValue("id"))
	if err != nil {
		erro(w, http.StatusBadRequest, "id inválido")
		return 0, false
	}
	return id, true
}

func (a API) listar(w http.ResponseWriter, _ *http.Request) { json_(w, 200, a.Store.Listar()) }

func (a API) criar(w http.ResponseWriter, r *http.Request) {
	i, err := lerItem(r)
	if err != nil {
		erro(w, http.StatusBadRequest, err.Error())
		return
	}
	novo := a.Store.Criar(i)
	w.Header().Set("Location", "/itens/"+strconv.Itoa(novo.ID))
	json_(w, http.StatusCreated, novo)
}

func (a API) obter(w http.ResponseWriter, r *http.Request) {
	id, ok := idDe(w, r)
	if !ok {
		return
	}
	i, err := a.Store.Obter(id)
	if err != nil {
		erro(w, http.StatusNotFound, err.Error())
		return
	}
	json_(w, 200, i)
}

func (a API) atualizar(w http.ResponseWriter, r *http.Request) {
	id, ok := idDe(w, r)
	if !ok {
		return
	}
	i, err := lerItem(r)
	if err != nil {
		erro(w, http.StatusBadRequest, err.Error())
		return
	}
	atual, err := a.Store.Atualizar(id, i)
	if err != nil {
		erro(w, http.StatusNotFound, err.Error())
		return
	}
	json_(w, 200, atual)
}

func (a API) remover(w http.ResponseWriter, r *http.Request) {
	id, ok := idDe(w, r)
	if !ok {
		return
	}
	if err := a.Store.Remover(id); err != nil {
		erro(w, http.StatusNotFound, err.Error())
		return
	}
	w.WriteHeader(http.StatusNoContent)
}
