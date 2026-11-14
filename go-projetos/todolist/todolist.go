// Pacote todolist implementa uma lista de tarefas com persistência em JSON.
package todolist

import (
	"encoding/json"
	"errors"
	"fmt"
	"os"
)

// Erros retornados pela lista.
var (
	ErrTituloVazio = errors.New("todolist: título vazio")
	ErrNaoExiste   = errors.New("todolist: tarefa não encontrada")
)

// Tarefa é um item da lista.
type Tarefa struct {
	ID     int    `json:"id"`
	Titulo string `json:"titulo"`
	Feita  bool   `json:"feita"`
}

// Lista guarda as tarefas e o próximo ID a ser usado.
type Lista struct {
	Tarefas   []Tarefa `json:"tarefas"`
	ProximoID int      `json:"proximo_id"`
}

// Nova cria uma lista vazia.
func Nova() *Lista {
	return &Lista{ProximoID: 1}
}

// Adicionar insere uma tarefa e devolve seu ID.
func (l *Lista) Adicionar(titulo string) (int, error) {
	if titulo == "" {
		return 0, ErrTituloVazio
	}
	id := l.ProximoID
	l.Tarefas = append(l.Tarefas, Tarefa{ID: id, Titulo: titulo})
	l.ProximoID++
	return id, nil
}

func (l *Lista) indice(id int) int {
	for i, t := range l.Tarefas {
		if t.ID == id {
			return i
		}
	}
	return -1
}

// Concluir marca a tarefa como feita.
func (l *Lista) Concluir(id int) error {
	i := l.indice(id)
	if i < 0 {
		return fmt.Errorf("%w: id %d", ErrNaoExiste, id)
	}
	l.Tarefas[i].Feita = true
	return nil
}

// Remover apaga a tarefa da lista.
func (l *Lista) Remover(id int) error {
	i := l.indice(id)
	if i < 0 {
		return fmt.Errorf("%w: id %d", ErrNaoExiste, id)
	}
	l.Tarefas = append(l.Tarefas[:i], l.Tarefas[i+1:]...)
	return nil
}

// Pendentes devolve as tarefas ainda não concluídas.
func (l *Lista) Pendentes() []Tarefa {
	var r []Tarefa
	for _, t := range l.Tarefas {
		if !t.Feita {
			r = append(r, t)
		}
	}
	return r
}

// Salvar grava a lista em um arquivo JSON.
func (l *Lista) Salvar(caminho string) error {
	dados, err := json.MarshalIndent(l, "", "  ")
	if err != nil {
		return err
	}
	return os.WriteFile(caminho, dados, 0o644)
}

// Carregar lê uma lista de um arquivo JSON.
func Carregar(caminho string) (*Lista, error) {
	dados, err := os.ReadFile(caminho)
	if err != nil {
		return nil, err
	}
	l := Nova()
	if err := json.Unmarshal(dados, l); err != nil {
		return nil, fmt.Errorf("todolist: JSON inválido: %w", err)
	}
	if l.ProximoID < 1 {
		l.ProximoID = 1
	}
	return l, nil
}
