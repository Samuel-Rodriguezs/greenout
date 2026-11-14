package skiplist

import (
	"math/rand"
	"sort"
	"sync"
	"testing"
)

func TestOperacoes(t *testing.T) {
	casos := []struct {
		nome   string
		chaves []int
	}{
		{"vazia", nil},
		{"uma", []int{5}},
		{"crescente", []int{1, 2, 3, 4, 5, 6, 7, 8}},
		{"decrescente", []int{8, 7, 6, 5, 4, 3, 2, 1}},
		{"negativos", []int{-3, 10, -7, 0, 4}},
		{"aleatoria", rand.New(rand.NewSource(9)).Perm(1000)},
	}
	for _, c := range casos {
		t.Run(c.nome, func(t *testing.T) {
			l := Nova[int, int](1)
			for _, k := range c.chaves {
				if !l.Inserir(k, k*3) {
					t.Fatalf("%d deveria ser nova", k)
				}
			}
			if l.Tamanho() != len(c.chaves) {
				t.Fatalf("tamanho = %d", l.Tamanho())
			}
			for _, k := range c.chaves {
				if v, ok := l.Buscar(k); !ok || v != k*3 {
					t.Fatalf("buscar %d = (%d,%v)", k, v, ok)
				}
			}
			ordenadas := append([]int(nil), c.chaves...)
			sort.Ints(ordenadas)
			var vistas []int
			l.Percorrer(func(k, _ int) bool { vistas = append(vistas, k); return true })
			if len(vistas) != len(ordenadas) {
				t.Fatalf("percurso incompleto")
			}
			for i := range vistas {
				if vistas[i] != ordenadas[i] {
					t.Fatal("percurso fora de ordem")
				}
			}
			for _, k := range c.chaves {
				if !l.Remover(k) {
					t.Fatalf("remover %d falhou", k)
				}
			}
			if l.Tamanho() != 0 {
				t.Fatal("deveria estar vazia")
			}
			if _, _, ok := l.Minimo(); ok {
				t.Fatal("mínimo de lista vazia")
			}
		})
	}
}

func TestSubstituirERemoverInexistente(t *testing.T) {
	l := Nova[string, int](2)
	l.Inserir("a", 1)
	if l.Inserir("a", 2) {
		t.Fatal("não deveria ser nova")
	}
	if v, _ := l.Buscar("a"); v != 2 {
		t.Fatalf("valor = %d", v)
	}
	if l.Remover("zzz") {
		t.Fatal("remover inexistente")
	}
	if _, ok := l.Buscar("zzz"); ok {
		t.Fatal("buscar inexistente")
	}
}

func TestIntervalo(t *testing.T) {
	l := Nova[int, int](3)
	for i := 0; i < 50; i += 5 {
		l.Inserir(i, i)
	}
	casos := []struct {
		nome    string
		de, ate int
		quer    int
	}{
		{"meio", 10, 30, 4},
		{"inicio ausente", 11, 30, 3},
		{"vazio", 20, 20, 0},
		{"invertido", 30, 10, 0},
		{"tudo", -10, 100, 10},
	}
	for _, c := range casos {
		n := 0
		l.Intervalo(c.de, c.ate, func(int, int) bool { n++; return true })
		if n != c.quer {
			t.Errorf("%s: visitou %d, quer %d", c.nome, n, c.quer)
		}
	}
	n := 0
	l.Percorrer(func(int, int) bool { n++; return n < 4 })
	if n != 4 {
		t.Fatalf("interrupção: %d", n)
	}
}

func TestMinimo(t *testing.T) {
	l := Nova[int, string](4)
	l.Inserir(9, "nove")
	l.Inserir(2, "dois")
	l.Inserir(5, "cinco")
	if k, v, ok := l.Minimo(); !ok || k != 2 || v != "dois" {
		t.Fatalf("mínimo = (%d,%q,%v)", k, v, ok)
	}
}

func TestContraMapaAleatorio(t *testing.T) {
	r := rand.New(rand.NewSource(5))
	l := Nova[int, int](5)
	ref := map[int]int{}
	for i := 0; i < 20000; i++ {
		k := r.Intn(400)
		if r.Intn(3) < 2 {
			_, ex := ref[k]
			if l.Inserir(k, i) == ex {
				t.Fatal("inserir inconsistente")
			}
			ref[k] = i
		} else {
			_, ex := ref[k]
			if l.Remover(k) != ex {
				t.Fatal("remover inconsistente")
			}
			delete(ref, k)
		}
	}
	if l.Tamanho() != len(ref) {
		t.Fatalf("tamanho %d != %d", l.Tamanho(), len(ref))
	}
	anterior := -1
	l.Percorrer(func(k, v int) bool {
		if k <= anterior || ref[k] != v {
			t.Fatalf("inconsistência na chave %d", k)
		}
		anterior = k
		return true
	})
}

func TestDeterminismoPorSemente(t *testing.T) {
	altura := func(sem int64) int {
		l := Nova[int, int](sem)
		for i := 0; i < 1000; i++ {
			l.Inserir(i, i)
		}
		return l.nivel
	}
	if altura(11) != altura(11) {
		t.Fatal("mesma semente deveria gerar mesma estrutura")
	}
	if a := altura(11); a < 4 || a > nivelMaximo {
		t.Fatalf("nível %d implausível para 1000 chaves", a)
	}
}

func TestConcorrencia(t *testing.T) {
	l := Nova[int, int](6)
	var wg sync.WaitGroup
	for g := 0; g < 8; g++ {
		wg.Add(1)
		go func(g int) {
			defer wg.Done()
			for i := 0; i < 300; i++ {
				k := g*1000 + i
				l.Inserir(k, k)
				l.Buscar(k)
				if i%3 == 0 {
					l.Remover(k)
				}
				l.Intervalo(0, 100, func(int, int) bool { return true })
			}
		}(g)
	}
	wg.Wait()
	if want := 8 * 200; l.Tamanho() != want {
		t.Fatalf("tamanho = %d, quer %d", l.Tamanho(), want)
	}
}
