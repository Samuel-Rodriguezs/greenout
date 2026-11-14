// Pacote todo implementa uma API completa de lista de tarefas:
//
//	GET    /tarefas?concluida=true|false&page=&per_page=
//	POST   /tarefas
//	GET    /tarefas/{id}
//	PUT    /tarefas/{id}
//	PATCH  /tarefas/{id}/concluir  (corpo opcional {"concluida": false})
//	DELETE /tarefas/{id}
package todo

import (
	"encoding/json"
	"errors"
	"net/http"
	"sort"
	"strconv"
	"strings"
	"sync"
	"time"
)

// Tarefa é um item da lista.
type Tarefa struct {
	ID           int       `json:"id"`
	Titulo       string    `json:"titulo"`
	Concluida    bool      `json:"concluida"`
	CriadaEm     time.Time `json:"criada_em"`
	AtualizadaEm time.Time `json:"atualizada_em"`
}

// ErrNaoEncontrada indica ID inexistente.
var ErrNaoEncontrada = errors.New("tarefa não encontrada")

// Lista guarda as tarefas em memória.
type Lista struct {
	Agora func() time.Time
	mu    sync.Mutex
	itens map[int]*Tarefa
	prox  int
}

// Nova cria uma lista vazia; agora nulo usa time.Now.
func Nova(agora func() time.Time) *Lista {
	if agora == nil {
		agora = time.Now
	}
	return &Lista{Agora: agora, itens: map[int]*Tarefa{}, prox: 1}
}

func validarTitulo(t string) (string, error) {
	t = strings.TrimSpace(t)
	if t == "" {
		return "", errors.New("título é obrigatório")
	}
	if len([]rune(t)) > 100 {
		return "", errors.New("título deve ter no máximo 100 caracteres")
	}
	return t, nil
}

// Adicionar cria uma tarefa.
func (l *Lista) Adicionar(titulo string) (Tarefa, error) {
	titulo, err := validarTitulo(titulo)
	if err != nil {
		return Tarefa{}, err
	}
	l.mu.Lock()
	defer l.mu.Unlock()
	agora := l.Agora()
	t := &Tarefa{ID: l.prox, Titulo: titulo, CriadaEm: agora, AtualizadaEm: agora}
	l.prox++
	l.itens[t.ID] = t
	return *t, nil
}

// Obter busca por ID.
func (l *Lista) Obter(id int) (Tarefa, error) {
	l.mu.Lock()
	defer l.mu.Unlock()
	t, ok := l.itens[id]
	if !ok {
		return Tarefa{}, ErrNaoEncontrada
	}
	return *t, nil
}

// Listar devolve as tarefas por ID; filtro nil lista todas.
func (l *Lista) Listar(concluida *bool) []Tarefa {
	l.mu.Lock()
	defer l.mu.Unlock()
	res := []Tarefa{}
	for _, t := range l.itens {
		if concluida == nil || t.Concluida == *concluida {
			res = append(res, *t)
		}
	}
	sort.Slice(res, func(a, b int) bool { return res[a].ID < res[b].ID })
	return res
}

func (l *Lista) mutar(id int, f func(*Tarefa)) (Tarefa, error) {
	l.mu.Lock()
	defer l.mu.Unlock()
	t, ok := l.itens[id]
	if !ok {
		return Tarefa{}, ErrNaoEncontrada
	}
	f(t)
	t.AtualizadaEm = l.Agora()
	return *t, nil
}

// Renomear altera o título.
func (l *Lista) Renomear(id int, titulo string) (Tarefa, error) {
	titulo, err := validarTitulo(titulo)
	if err != nil {
		return Tarefa{}, err
	}
	return l.mutar(id, func(t *Tarefa) { t.Titulo = titulo })
}

// Marcar define o estado de conclusão.
func (l *Lista) Marcar(id int, concluida bool) (Tarefa, error) {
	return l.mutar(id, func(t *Tarefa) { t.Concluida = concluida })
}

// Remover apaga a tarefa.
func (l *Lista) Remover(id int) error {
	l.mu.Lock()
	defer l.mu.Unlock()
	if _, ok := l.itens[id]; !ok {
		return ErrNaoEncontrada
	}
	delete(l.itens, id)
	return nil
}

// Handler expõe a lista via HTTP.
func (l *Lista) Handler() http.Handler {
	m := http.NewServeMux()
	m.HandleFunc("GET /tarefas", l.hListar)
	m.HandleFunc("POST /tarefas", l.hCriar)
	m.HandleFunc("GET /tarefas/{id}", l.hObter)
	m.HandleFunc("PUT /tarefas/{id}", l.hAtualizar)
	m.HandleFunc("PATCH /tarefas/{id}/concluir", l.hConcluir)
	m.HandleFunc("DELETE /tarefas/{id}", l.hRemover)
	return m
}

func resp(w http.ResponseWriter, status int, v any) {
	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(status)
	json.NewEncoder(w).Encode(v)
}

func falha(w http.ResponseWriter, status int, msg string) {
	resp(w, status, map[string]string{"erro": msg})
}

func tratar(w http.ResponseWriter, err error) {
	if errors.Is(err, ErrNaoEncontrada) {
		falha(w, http.StatusNotFound, err.Error())
		return
	}
	falha(w, http.StatusBadRequest, err.Error())
}

func idDe(w http.ResponseWriter, r *http.Request) (int, bool) {
	id, err := strconv.Atoi(r.PathValue("id"))
	if err != nil || id < 1 {
		falha(w, http.StatusBadRequest, "id inválido")
		return 0, false
	}
	return id, true
}

type entradaTitulo struct {
	Titulo string `json:"titulo"`
}

func lerJSON(w http.ResponseWriter, r *http.Request, v any) bool {
	if err := json.NewDecoder(http.MaxBytesReader(w, r.Body, 1<<16)).Decode(v); err != nil {
		falha(w, http.StatusBadRequest, "JSON inválido")
		return false
	}
	return true
}

func (l *Lista) hListar(w http.ResponseWriter, r *http.Request) {
	var filtro *bool
	if s := r.URL.Query().Get("concluida"); s != "" {
		b, err := strconv.ParseBool(s)
		if err != nil {
			falha(w, http.StatusBadRequest, "concluida deve ser true ou false")
			return
		}
		filtro = &b
	}
	todas := l.Listar(filtro)
	pagina, _ := strconv.Atoi(r.URL.Query().Get("page"))
	por, _ := strconv.Atoi(r.URL.Query().Get("per_page"))
	if pagina < 1 {
		pagina = 1
	}
	if por < 1 || por > 100 {
		por = 20
	}
	ini := min((pagina-1)*por, len(todas))
	fim := min(ini+por, len(todas))
	w.Header().Set("X-Total-Count", strconv.Itoa(len(todas)))
	resp(w, http.StatusOK, todas[ini:fim])
}

func (l *Lista) hCriar(w http.ResponseWriter, r *http.Request) {
	var e entradaTitulo
	if !lerJSON(w, r, &e) {
		return
	}
	t, err := l.Adicionar(e.Titulo)
	if err != nil {
		tratar(w, err)
		return
	}
	w.Header().Set("Location", "/tarefas/"+strconv.Itoa(t.ID))
	resp(w, http.StatusCreated, t)
}

func (l *Lista) hObter(w http.ResponseWriter, r *http.Request) {
	id, ok := idDe(w, r)
	if !ok {
		return
	}
	t, err := l.Obter(id)
	if err != nil {
		tratar(w, err)
		return
	}
	resp(w, http.StatusOK, t)
}

func (l *Lista) hAtualizar(w http.ResponseWriter, r *http.Request) {
	id, ok := idDe(w, r)
	if !ok {
		return
	}
	var e entradaTitulo
	if !lerJSON(w, r, &e) {
		return
	}
	t, err := l.Renomear(id, e.Titulo)
	if err != nil {
		tratar(w, err)
		return
	}
	resp(w, http.StatusOK, t)
}

func (l *Lista) hConcluir(w http.ResponseWriter, r *http.Request) {
	id, ok := idDe(w, r)
	if !ok {
		return
	}
	estado := true
	if r.ContentLength != 0 {
		var e struct {
			Concluida *bool `json:"concluida"`
		}
		if !lerJSON(w, r, &e) {
			return
		}
		if e.Concluida != nil {
			estado = *e.Concluida
		}
	}
	t, err := l.Marcar(id, estado)
	if err != nil {
		tratar(w, err)
		return
	}
	resp(w, http.StatusOK, t)
}

func (l *Lista) hRemover(w http.ResponseWriter, r *http.Request) {
	id, ok := idDe(w, r)
	if !ok {
		return
	}
	if err := l.Remover(id); err != nil {
		tratar(w, err)
		return
	}
	w.WriteHeader(http.StatusNoContent)
}
