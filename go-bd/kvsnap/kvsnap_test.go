package kvsnap

import (
	"fmt"
	"reflect"
	"sync"
	"testing"
)

func TestOperacoesBasicas(t *testing.T) {
	casos := []struct {
		nome   string
		passos func(l *Loja)
		chave  string
		quer   string
		existe bool
	}{
		{"vazio", func(l *Loja) {}, "a", "", false},
		{"definir", func(l *Loja) { l.Definir("a", "1") }, "a", "1", true},
		{"sobrescrever", func(l *Loja) { l.Definir("a", "1"); l.Definir("a", "2") }, "a", "2", true},
		{"remover", func(l *Loja) { l.Definir("a", "1"); l.Remover("a") }, "a", "", false},
		{"valor vazio existe", func(l *Loja) { l.Definir("a", "") }, "a", "", true},
	}
	for _, c := range casos {
		t.Run(c.nome, func(t *testing.T) {
			l := Nova()
			c.passos(l)
			v, ok := l.Obter(c.chave)
			if v != c.quer || ok != c.existe {
				t.Fatalf("obteve (%q,%v), quer (%q,%v)", v, ok, c.quer, c.existe)
			}
		})
	}
}

func TestRemoverInexistente(t *testing.T) {
	if Nova().Remover("x") {
		t.Fatal("remover chave inexistente deveria devolver false")
	}
}

func TestSnapshotIsolado(t *testing.T) {
	l := Nova()
	l.Definir("a", "1")
	l.Definir("b", "2")
	id := l.Snapshot()
	l.Definir("a", "9")
	l.Remover("b")
	l.Definir("c", "3")

	if v, ok, err := l.ObterEm(id, "a"); err != nil || !ok || v != "1" {
		t.Fatalf("snapshot a = (%q,%v,%v)", v, ok, err)
	}
	if v, ok, _ := l.ObterEm(id, "b"); !ok || v != "2" {
		t.Fatalf("snapshot b = (%q,%v)", v, ok)
	}
	if _, ok, _ := l.ObterEm(id, "c"); ok {
		t.Fatal("snapshot não deve ver chave nova")
	}
}

func TestRestaurar(t *testing.T) {
	l := Nova()
	l.Definir("a", "1")
	id := l.Snapshot()
	l.Definir("a", "2")
	l.Definir("z", "9")
	if err := l.Restaurar(id); err != nil {
		t.Fatal(err)
	}
	if got := l.Chaves(); !reflect.DeepEqual(got, []string{"a"}) {
		t.Fatalf("chaves = %v", got)
	}
	// alterar depois de restaurar não pode contaminar o snapshot
	l.Definir("a", "novo")
	if v, _, _ := l.ObterEm(id, "a"); v != "1" {
		t.Fatalf("snapshot contaminado: %q", v)
	}
}

func TestSnapshotInexistente(t *testing.T) {
	l := Nova()
	if _, _, err := l.ObterEm(42, "a"); err != ErrSnapshotInexistente {
		t.Fatalf("err = %v", err)
	}
	if err := l.Restaurar(42); err != ErrSnapshotInexistente {
		t.Fatalf("err = %v", err)
	}
	id := l.Snapshot()
	if err := l.Descartar(id); err != nil {
		t.Fatal(err)
	}
	if err := l.Descartar(id); err != ErrSnapshotInexistente {
		t.Fatalf("descartar duas vezes: %v", err)
	}
}

func TestConcorrencia(t *testing.T) {
	l := Nova()
	var wg sync.WaitGroup
	for g := 0; g < 8; g++ {
		wg.Add(1)
		go func(g int) {
			defer wg.Done()
			for i := 0; i < 200; i++ {
				l.Definir(fmt.Sprintf("g%d-%d", g, i), "v")
				if i%50 == 0 {
					id := l.Snapshot()
					l.ObterEm(id, "x")
					l.Descartar(id)
				}
				l.Obter("g0-0")
			}
		}(g)
	}
	wg.Wait()
	if l.Tamanho() != 8*200 {
		t.Fatalf("tamanho = %d", l.Tamanho())
	}
}
