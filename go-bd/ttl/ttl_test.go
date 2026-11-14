package ttl

import (
	"fmt"
	"sync"
	"testing"
	"time"
)

var inicio = time.Date(2026, 1, 1, 12, 0, 0, 0, time.UTC)

func nova() (*Loja, *RelogioFalso) {
	r := NovoRelogioFalso(inicio)
	return Nova(r), r
}

func TestExpiracao(t *testing.T) {
	casos := []struct {
		nome   string
		ttl    time.Duration
		avanca time.Duration
		vivo   bool
	}{
		{"sem ttl nunca expira", 0, 1000 * time.Hour, true},
		{"antes de expirar", 10 * time.Second, 9 * time.Second, true},
		{"1ns antes", 10 * time.Second, 10*time.Second - 1, true},
		{"no instante exato", 10 * time.Second, 10 * time.Second, false},
		{"depois", 10 * time.Second, time.Minute, false},
		{"sem avanço", time.Second, 0, true},
	}
	for _, c := range casos {
		t.Run(c.nome, func(t *testing.T) {
			l, r := nova()
			l.Definir("k", "v", c.ttl)
			r.Avancar(c.avanca)
			v, ok := l.Obter("k")
			if ok != c.vivo || (ok && v != "v") {
				t.Fatalf("Obter = (%q,%v), vivo esperado %v", v, ok, c.vivo)
			}
		})
	}
}

func TestTTLNegativo(t *testing.T) {
	l, _ := nova()
	if err := l.Definir("k", "v", -time.Second); err != ErrTTLInvalido {
		t.Fatalf("err = %v", err)
	}
	if _, ok := l.Obter("k"); ok {
		t.Fatal("não deveria ter gravado")
	}
}

func TestRestante(t *testing.T) {
	l, r := nova()
	l.Definir("a", "1", 30*time.Second)
	l.Definir("b", "2", 0)
	r.Avancar(10 * time.Second)

	if rest, tem, ex := l.TTL("a"); !ex || !tem || rest != 20*time.Second {
		t.Fatalf("a: %v %v %v", rest, tem, ex)
	}
	if _, tem, ex := l.TTL("b"); !ex || tem {
		t.Fatalf("b: tem=%v ex=%v", tem, ex)
	}
	if _, _, ex := l.TTL("zzz"); ex {
		t.Fatal("zzz não existe")
	}
	r.Avancar(time.Minute)
	if _, _, ex := l.TTL("a"); ex {
		t.Fatal("a deveria ter expirado")
	}
}

func TestSobrescreverRenovaTTL(t *testing.T) {
	l, r := nova()
	l.Definir("k", "v1", 10*time.Second)
	r.Avancar(8 * time.Second)
	l.Definir("k", "v2", 10*time.Second)
	r.Avancar(8 * time.Second)
	if v, ok := l.Obter("k"); !ok || v != "v2" {
		t.Fatalf("Obter = (%q,%v)", v, ok)
	}
	// sobrescrever sem ttl torna a chave permanente
	l.Definir("k", "v3", 0)
	r.Avancar(time.Hour)
	if _, ok := l.Obter("k"); !ok {
		t.Fatal("chave sem ttl deveria permanecer")
	}
}

func TestExpirarEPersistir(t *testing.T) {
	l, r := nova()
	if l.Expirar("ausente", time.Second) || l.Persistir("ausente") {
		t.Fatal("operações em chave ausente")
	}
	l.Definir("k", "v", 0)
	if l.Persistir("k") {
		t.Fatal("persistir sem ttl devolve false")
	}
	if !l.Expirar("k", 5*time.Second) {
		t.Fatal("expirar")
	}
	r.Avancar(3 * time.Second)
	if !l.Persistir("k") {
		t.Fatal("persistir com ttl devolve true")
	}
	r.Avancar(time.Hour)
	if _, ok := l.Obter("k"); !ok {
		t.Fatal("chave persistida deveria sobreviver")
	}
	if !l.Expirar("k", 0) {
		t.Fatal("expirar com 0 apaga")
	}
	if _, ok := l.Obter("k"); ok {
		t.Fatal("chave deveria ter sido apagada")
	}
}

func TestRemover(t *testing.T) {
	l, r := nova()
	l.Definir("a", "1", time.Second)
	l.Definir("b", "2", 0)
	r.Avancar(2 * time.Second)
	if l.Remover("a") {
		t.Fatal("remover chave expirada devolve false")
	}
	if !l.Remover("b") || l.Remover("b") {
		t.Fatal("remover b")
	}
}

func TestVarrerETamanho(t *testing.T) {
	l, r := nova()
	for i := 0; i < 10; i++ {
		l.Definir(fmt.Sprint("curta", i), "v", time.Second)
		l.Definir(fmt.Sprint("longa", i), "v", time.Hour)
	}
	l.Definir("eterna", "v", 0)
	if l.Tamanho() != 21 {
		t.Fatalf("tamanho = %d", l.Tamanho())
	}
	r.Avancar(2 * time.Second)
	if l.Tamanho() != 11 {
		t.Fatalf("tamanho após expirar = %d", l.Tamanho())
	}
	if n := l.Varrer(); n != 10 {
		t.Fatalf("varreu %d", n)
	}
	if n := l.Varrer(); n != 0 {
		t.Fatalf("segunda varredura %d", n)
	}
	if len(l.dados) != 11 {
		t.Fatalf("mapa interno com %d itens", len(l.dados))
	}
}

func TestRelogioFalso(t *testing.T) {
	r := NovoRelogioFalso(inicio)
	r.Avancar(time.Hour)
	r.Avancar(-30 * time.Minute)
	if got := r.Agora(); !got.Equal(inicio.Add(30 * time.Minute)) {
		t.Fatalf("agora = %v", got)
	}
}

func TestRelogioRealPadrao(t *testing.T) {
	l := Nova(nil)
	l.Definir("k", "v", time.Hour)
	if _, ok := l.Obter("k"); !ok {
		t.Fatal("chave recém-criada com ttl longo deveria existir")
	}
	l.Definir("e", "v", time.Nanosecond)
	time.Sleep(time.Millisecond)
	if _, ok := l.Obter("e"); ok {
		t.Fatal("ttl de 1ns deveria ter vencido")
	}
}

func TestConcorrencia(t *testing.T) {
	l, r := nova()
	var wg sync.WaitGroup
	for g := 0; g < 8; g++ {
		wg.Add(1)
		go func(g int) {
			defer wg.Done()
			for i := 0; i < 300; i++ {
				k := fmt.Sprintf("k%d", i%20)
				l.Definir(k, "v", time.Second)
				l.Obter(k)
				l.TTL(k)
				if i%50 == 0 {
					r.Avancar(500 * time.Millisecond)
					l.Varrer()
				}
				l.Tamanho()
			}
		}(g)
	}
	wg.Wait()
}
