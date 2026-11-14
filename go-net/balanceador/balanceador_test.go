package balanceador

import (
	"errors"
	"fmt"
	"reflect"
	"sync"
	"testing"
)

func TestRoundRobin(t *testing.T) {
	r := NovoRoundRobin("a", "b", "c")
	var got []string
	for i := 0; i < 7; i++ {
		b, err := r.Proximo()
		if err != nil {
			t.Fatal(err)
		}
		got = append(got, b)
	}
	if want := []string{"a", "b", "c", "a", "b", "c", "a"}; !reflect.DeepEqual(got, want) {
		t.Errorf("sequência = %v", got)
	}
}

func TestRoundRobinVazioERemocao(t *testing.T) {
	if _, err := NovoRoundRobin().Proximo(); !errors.Is(err, ErrSemBackends) {
		t.Errorf("vazio: %v", err)
	}
	r := NovoRoundRobin("a", "b", "c")
	r.Proximo() // a
	r.Proximo() // b ; próximo seria c
	if !r.Remover("a") || r.Remover("zzz") {
		t.Fatal("Remover")
	}
	// Remover "a" (antes do cursor) não deve pular "c".
	if b, _ := r.Proximo(); b != "c" {
		t.Errorf("esperava c, veio %s", b)
	}
	if b, _ := r.Proximo(); b != "b" {
		t.Errorf("esperava b, veio %s", b)
	}
	r.Remover("b")
	r.Remover("c")
	if _, err := r.Proximo(); !errors.Is(err, ErrSemBackends) {
		t.Errorf("após remover tudo: %v", err)
	}
}

func TestRoundRobinCopiaEntrada(t *testing.T) {
	lista := []string{"a", "b"}
	r := NovoRoundRobin(lista...)
	lista[0] = "x"
	if b, _ := r.Proximo(); b != "a" {
		t.Errorf("não copiou a lista: %s", b)
	}
}

func TestMenosConexoes(t *testing.T) {
	m := NovoMenosConexoes("a", "b", "c")
	var escolhas []string
	for i := 0; i < 3; i++ {
		b, _ := m.Adquirir()
		escolhas = append(escolhas, b)
	}
	if !reflect.DeepEqual(escolhas, []string{"a", "b", "c"}) {
		t.Errorf("empates por ordem: %v", escolhas)
	}
	m.Adquirir() // a=2
	m.Adquirir() // b=2
	if err := m.Liberar("c"); err != nil {
		t.Fatal(err)
	}
	if b, _ := m.Adquirir(); b != "c" { // c=0 é o menor
		t.Errorf("deveria escolher c, veio %s", b)
	}
	if m.Ativas("a") != 2 || m.Ativas("b") != 2 || m.Ativas("c") != 1 {
		t.Errorf("ativas a=%d b=%d c=%d", m.Ativas("a"), m.Ativas("b"), m.Ativas("c"))
	}
}

func TestMenosConexoesErros(t *testing.T) {
	if _, err := NovoMenosConexoes().Adquirir(); !errors.Is(err, ErrSemBackends) {
		t.Errorf("vazio: %v", err)
	}
	m := NovoMenosConexoes("a")
	if err := m.Liberar("a"); err == nil {
		t.Error("liberar sem adquirir deveria falhar")
	}
	if err := m.Liberar("desconhecido"); err == nil {
		t.Error("liberar backend desconhecido deveria falhar")
	}
}

func TestMenosConexoesConcorrente(t *testing.T) {
	m := NovoMenosConexoes("a", "b", "c", "d")
	var wg sync.WaitGroup
	for i := 0; i < 8; i++ {
		wg.Add(1)
		go func() {
			defer wg.Done()
			for j := 0; j < 100; j++ {
				b, _ := m.Adquirir()
				m.Liberar(b)
			}
		}()
	}
	wg.Wait()
	for _, b := range []string{"a", "b", "c", "d"} {
		if m.Ativas(b) != 0 {
			t.Errorf("%s com %d conexões vazadas", b, m.Ativas(b))
		}
	}
}

func chaves(n int) []string {
	out := make([]string, n)
	for i := range out {
		out[i] = fmt.Sprintf("usuario-%d", i)
	}
	return out
}

func TestHashConsistenteDeterministico(t *testing.T) {
	a := NovoHashConsistente(50, "s1", "s2", "s3")
	b := NovoHashConsistente(50, "s3", "s1", "s2") // ordem de inserção diferente
	for _, k := range chaves(200) {
		x, _ := a.Buscar(k)
		y, _ := b.Buscar(k)
		if x != y {
			t.Fatalf("chave %s: %s != %s", k, x, y)
		}
		if z, _ := a.Buscar(k); z != x {
			t.Fatal("mesma chave deve dar sempre o mesmo backend")
		}
	}
}

func TestHashConsistenteDistribuicao(t *testing.T) {
	h := NovoHashConsistente(100, "s1", "s2", "s3", "s4")
	cont := map[string]int{}
	const n = 8000
	for _, k := range chaves(n) {
		b, _ := h.Buscar(k)
		cont[b]++
	}
	for b, c := range cont {
		if c < n/4/2 || c > n/4*2 { // dentro de 50%..200% do ideal
			t.Errorf("%s recebeu %d de %d chaves (desequilíbrio)", b, c, n)
		}
	}
	if len(cont) != 4 {
		t.Errorf("backends usados: %d", len(cont))
	}
}

func TestHashConsistenteMinimaMovimentacao(t *testing.T) {
	h := NovoHashConsistente(100, "s1", "s2", "s3", "s4")
	antes := map[string]string{}
	ks := chaves(4000)
	for _, k := range ks {
		antes[k], _ = h.Buscar(k)
	}
	// Remover s2: só chaves que estavam em s2 podem mudar.
	if !h.Remover("s2") || h.Remover("s2") {
		t.Fatal("Remover")
	}
	for _, k := range ks {
		depois, _ := h.Buscar(k)
		if antes[k] != "s2" && depois != antes[k] {
			t.Fatalf("chave %s moveu de %s para %s sem necessidade", k, antes[k], depois)
		}
		if depois == "s2" {
			t.Fatalf("chave %s ainda em s2", k)
		}
	}
	// Adicionar s5: chaves só podem mover para s5.
	meio := map[string]string{}
	for _, k := range ks {
		meio[k], _ = h.Buscar(k)
	}
	h.Adicionar("s5")
	h.Adicionar("s5") // idempotente
	movidas := 0
	for _, k := range ks {
		depois, _ := h.Buscar(k)
		if depois != meio[k] {
			movidas++
			if depois != "s5" {
				t.Fatalf("chave %s moveu para %s, esperava s5", k, depois)
			}
		}
	}
	if movidas == 0 || movidas > len(ks)/2 {
		t.Errorf("movidas = %d de %d", movidas, len(ks))
	}
}

func TestHashConsistenteVazio(t *testing.T) {
	h := NovoHashConsistente(0)
	if _, err := h.Buscar("x"); !errors.Is(err, ErrSemBackends) {
		t.Errorf("anel vazio: %v", err)
	}
	h.Adicionar("unico")
	if b, _ := h.Buscar("qualquer"); b != "unico" {
		t.Errorf("único backend: %s", b)
	}
	h.Remover("unico")
	if _, err := h.Buscar("x"); !errors.Is(err, ErrSemBackends) {
		t.Errorf("após remover: %v", err)
	}
}

func TestHashConsistenteConcorrente(t *testing.T) {
	h := NovoHashConsistente(20, "a", "b")
	var wg sync.WaitGroup
	for i := 0; i < 4; i++ {
		wg.Add(2)
		go func() {
			defer wg.Done()
			for j := 0; j < 200; j++ {
				h.Buscar(fmt.Sprint(j))
			}
		}()
		go func(i int) {
			defer wg.Done()
			n := fmt.Sprintf("x%d", i)
			h.Adicionar(n)
			h.Remover(n)
		}(i)
	}
	wg.Wait()
}
