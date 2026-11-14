package indicehash

import (
	"fmt"
	"reflect"
	"sync"
	"testing"
)

func TestInserirBuscar(t *testing.T) {
	casos := []struct {
		nome  string
		ins   [][2]any
		chave string
		quer  []uint64
	}{
		{"ausente", nil, "a", nil},
		{"um", [][2]any{{"a", uint64(1)}}, "a", []uint64{1}},
		{"nao unico", [][2]any{{"a", uint64(1)}, {"a", uint64(2)}, {"b", uint64(9)}}, "a", []uint64{1, 2}},
		{"duplicado ignorado", [][2]any{{"a", uint64(1)}, {"a", uint64(1)}}, "a", []uint64{1}},
		{"chave vazia", [][2]any{{"", uint64(7)}}, "", []uint64{7}},
	}
	for _, c := range casos {
		t.Run(c.nome, func(t *testing.T) {
			x := Novo()
			for _, p := range c.ins {
				x.Inserir(p[0].(string), p[1].(uint64))
			}
			if got := x.Buscar(c.chave); !reflect.DeepEqual(got, c.quer) {
				t.Fatalf("got %v, quer %v", got, c.quer)
			}
		})
	}
}

func TestContagensEDuplicado(t *testing.T) {
	x := Novo()
	if !x.Inserir("a", 1) || x.Inserir("a", 1) || !x.Inserir("a", 2) || !x.Inserir("b", 1) {
		t.Fatal("retornos de Inserir inesperados")
	}
	if x.NumChaves() != 2 || x.NumPares() != 3 {
		t.Fatalf("chaves=%d pares=%d", x.NumChaves(), x.NumPares())
	}
}

func TestBuscarDevolveCopia(t *testing.T) {
	x := Novo()
	x.Inserir("k", 1)
	r := x.Buscar("k")
	r[0] = 999
	if got := x.Buscar("k"); got[0] != 1 {
		t.Fatal("alterar o resultado afetou o índice")
	}
}

func TestRemover(t *testing.T) {
	x := Novo()
	x.Inserir("a", 1)
	x.Inserir("a", 2)
	x.Inserir("a", 3)
	if !x.Remover("a", 2) {
		t.Fatal("remover existente")
	}
	if x.Remover("a", 2) || x.Remover("zzz", 1) {
		t.Fatal("remover inexistente deveria devolver false")
	}
	if got := x.Buscar("a"); !reflect.DeepEqual(got, []uint64{1, 3}) {
		t.Fatalf("got %v", got)
	}
	x.Remover("a", 1)
	x.Remover("a", 3)
	if x.NumChaves() != 0 || x.NumPares() != 0 || x.Buscar("a") != nil {
		t.Fatal("chave sem RIDs deveria sumir")
	}
}

func TestRemoverChave(t *testing.T) {
	x := Novo()
	x.Inserir("a", 1)
	x.Inserir("a", 2)
	x.Inserir("b", 3)
	if n := x.RemoverChave("a"); n != 2 {
		t.Fatalf("n = %d", n)
	}
	if n := x.RemoverChave("a"); n != 0 {
		t.Fatalf("n = %d", n)
	}
	if x.NumChaves() != 1 || x.NumPares() != 1 {
		t.Fatalf("chaves=%d pares=%d", x.NumChaves(), x.NumPares())
	}
}

func TestCrescimentoPreservaDados(t *testing.T) {
	x := Novo()
	const n = 5000
	for i := 0; i < n; i++ {
		x.Inserir(fmt.Sprintf("chave-%d", i), uint64(i))
		x.Inserir(fmt.Sprintf("chave-%d", i), uint64(i+n))
	}
	if x.NumChaves() != n || x.NumPares() != 2*n {
		t.Fatalf("chaves=%d pares=%d", x.NumChaves(), x.NumPares())
	}
	for i := 0; i < n; i++ {
		if got := x.Buscar(fmt.Sprintf("chave-%d", i)); !reflect.DeepEqual(got, []uint64{uint64(i), uint64(i + n)}) {
			t.Fatalf("chave-%d = %v", i, got)
		}
	}
	if len(x.baldes) < n {
		t.Fatalf("baldes = %d, deveria ter crescido", len(x.baldes))
	}
}

func TestRemoverNoMeioDaCadeia(t *testing.T) {
	x := Novo()
	// força colisões usando muitos itens em poucos baldes
	for i := 0; i < 6; i++ {
		x.Inserir(fmt.Sprint("k", i), uint64(i))
	}
	for i := 0; i < 6; i++ {
		x.RemoverChave(fmt.Sprint("k", i))
		for j := i + 1; j < 6; j++ {
			if x.Buscar(fmt.Sprint("k", j)) == nil {
				t.Fatalf("k%d sumiu ao remover k%d", j, i)
			}
		}
	}
	if x.NumChaves() != 0 {
		t.Fatal("deveria estar vazio")
	}
}

func TestConcorrencia(t *testing.T) {
	x := Novo()
	var wg sync.WaitGroup
	for g := 0; g < 8; g++ {
		wg.Add(1)
		go func(g int) {
			defer wg.Done()
			for i := 0; i < 300; i++ {
				k := fmt.Sprintf("k%d", i%50)
				x.Inserir(k, uint64(g*1000+i))
				x.Buscar(k)
				if i%7 == 0 {
					x.Remover(k, uint64(g*1000+i))
				}
			}
		}(g)
	}
	wg.Wait()
	if x.NumChaves() != 50 {
		t.Fatalf("chaves = %d", x.NumChaves())
	}
}
