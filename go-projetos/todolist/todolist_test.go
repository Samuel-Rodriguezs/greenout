package todolist

import (
	"errors"
	"os"
	"path/filepath"
	"testing"
)

func TestAdicionar(t *testing.T) {
	casos := []struct {
		nome   string
		titulo string
		err    error
	}{
		{"valido", "comprar pão", nil},
		{"vazio", "", ErrTituloVazio},
	}
	for _, c := range casos {
		t.Run(c.nome, func(t *testing.T) {
			l := Nova()
			_, err := l.Adicionar(c.titulo)
			if !errors.Is(err, c.err) {
				t.Fatalf("erro = %v, esperado %v", err, c.err)
			}
		})
	}
}

func TestConcluirRemoverPendentes(t *testing.T) {
	l := Nova()
	a, _ := l.Adicionar("a")
	b, _ := l.Adicionar("b")
	l.Adicionar("c")
	if err := l.Concluir(a); err != nil {
		t.Fatal(err)
	}
	if err := l.Remover(b); err != nil {
		t.Fatal(err)
	}
	p := l.Pendentes()
	if len(p) != 1 || p[0].Titulo != "c" {
		t.Fatalf("pendentes inesperados: %+v", p)
	}
	if !errors.Is(l.Concluir(99), ErrNaoExiste) {
		t.Error("esperava ErrNaoExiste em Concluir")
	}
	if !errors.Is(l.Remover(99), ErrNaoExiste) {
		t.Error("esperava ErrNaoExiste em Remover")
	}
}

func TestPersistencia(t *testing.T) {
	caminho := filepath.Join(t.TempDir(), "lista.json")
	l := Nova()
	l.Adicionar("x")
	id, _ := l.Adicionar("y")
	l.Concluir(id)
	if err := l.Salvar(caminho); err != nil {
		t.Fatal(err)
	}
	c, err := Carregar(caminho)
	if err != nil {
		t.Fatal(err)
	}
	if len(c.Tarefas) != 2 || !c.Tarefas[1].Feita {
		t.Fatalf("dados perdidos: %+v", c)
	}
	novo, _ := c.Adicionar("z")
	if novo != 3 {
		t.Errorf("próximo ID = %d, esperado 3", novo)
	}
}

func TestCarregarErros(t *testing.T) {
	dir := t.TempDir()
	if _, err := Carregar(filepath.Join(dir, "nao-existe.json")); err == nil {
		t.Error("esperava erro para arquivo ausente")
	}
	ruim := filepath.Join(dir, "ruim.json")
	os.WriteFile(ruim, []byte("{não é json"), 0o644)
	if _, err := Carregar(ruim); err == nil {
		t.Error("esperava erro para JSON inválido")
	}
}
