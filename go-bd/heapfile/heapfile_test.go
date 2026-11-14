package heapfile

import (
	"bytes"
	"fmt"
	"math/rand"
	"os"
	"path/filepath"
	"sync"
	"testing"

	"greenout/bd/pagina"
)

func novo(t *testing.T) (*Arquivo, string) {
	t.Helper()
	p := filepath.Join(t.TempDir(), "heap.db")
	a, err := Abrir(p)
	if err != nil {
		t.Fatal(err)
	}
	t.Cleanup(func() { a.Fechar() })
	return a, p
}

func TestInserirLer(t *testing.T) {
	casos := []struct {
		nome string
		dado []byte
	}{
		{"curto", []byte("ola")},
		{"vazio", []byte{}},
		{"binario", []byte{0, 255, 0, 1}},
		{"grande", bytes.Repeat([]byte("g"), 3000)},
		{"maximo", make([]byte, pagina.MaxRegistro)},
	}
	a, _ := novo(t)
	rids := make([]RID, len(casos))
	for i, c := range casos {
		r, err := a.Inserir(c.dado)
		if err != nil {
			t.Fatalf("%s: %v", c.nome, err)
		}
		rids[i] = r
	}
	for i, c := range casos {
		got, err := a.Ler(rids[i])
		if err != nil || !bytes.Equal(got, c.dado) {
			t.Fatalf("%s: %v", c.nome, err)
		}
	}
}

func TestRegistroGrandeDemais(t *testing.T) {
	a, _ := novo(t)
	if _, err := a.Inserir(make([]byte, pagina.MaxRegistro+1)); err != ErrGrande {
		t.Fatalf("err = %v", err)
	}
}

func TestMultiplasPaginasERIDsEstaveis(t *testing.T) {
	a, _ := novo(t)
	var rids []RID
	for i := 0; i < 200; i++ {
		r, err := a.Inserir([]byte(fmt.Sprintf("registro-%04d-%s", i, bytes.Repeat([]byte("x"), 200))))
		if err != nil {
			t.Fatal(err)
		}
		rids = append(rids, r)
	}
	if a.NumPaginas() < 5 {
		t.Fatalf("páginas = %d", a.NumPaginas())
	}
	for i, r := range rids {
		got, _ := a.Ler(r)
		if !bytes.HasPrefix(got, []byte(fmt.Sprintf("registro-%04d", i))) {
			t.Fatalf("RID %v devolveu %q", r, got[:20])
		}
	}
}

func TestRemoverEReusarEspaco(t *testing.T) {
	a, _ := novo(t)
	r1, _ := a.Inserir(bytes.Repeat([]byte("a"), 2000))
	r2, _ := a.Inserir(bytes.Repeat([]byte("b"), 2000))
	if r1.Pagina != r2.Pagina {
		t.Fatal("deveriam caber na mesma página")
	}
	if err := a.Remover(r1); err != nil {
		t.Fatal(err)
	}
	if _, err := a.Ler(r1); err == nil {
		t.Fatal("ler removido deveria falhar")
	}
	if err := a.Remover(r1); err == nil {
		t.Fatal("remover duas vezes deveria falhar")
	}
	r3, _ := a.Inserir(bytes.Repeat([]byte("c"), 2000))
	if r3.Pagina != r1.Pagina || a.NumPaginas() != 1 {
		t.Fatalf("espaço liberado não reaproveitado: %v, páginas=%d", r3, a.NumPaginas())
	}
}

func TestRIDInvalido(t *testing.T) {
	a, _ := novo(t)
	a.Inserir([]byte("x"))
	for _, r := range []RID{{5, 0}, {0, 9}} {
		if _, err := a.Ler(r); err == nil {
			t.Fatalf("ler %v deveria falhar", r)
		}
	}
	if _, err := a.Ler(RID{5, 0}); err != ErrRIDInvalido {
		t.Fatalf("err = %v", err)
	}
	if err := a.Remover(RID{9, 0}); err != ErrRIDInvalido {
		t.Fatalf("err = %v", err)
	}
	if _, err := a.Atualizar(RID{9, 0}, []byte("x")); err != ErrRIDInvalido {
		t.Fatalf("err = %v", err)
	}
}

func TestAtualizarNoLugarEMovendo(t *testing.T) {
	a, _ := novo(t)
	r, _ := a.Inserir([]byte("pequeno"))
	n, err := a.Atualizar(r, []byte("peq"))
	if err != nil || n != r {
		t.Fatalf("no lugar: %v %v", n, err)
	}
	// enche a página para forçar a migração
	a.Inserir(bytes.Repeat([]byte("f"), 3900))
	n, err = a.Atualizar(r, bytes.Repeat([]byte("g"), 2000))
	if err != nil {
		t.Fatal(err)
	}
	if n == r {
		t.Fatal("registro deveria ter migrado de página")
	}
	got, _ := a.Ler(n)
	if !bytes.Equal(got, bytes.Repeat([]byte("g"), 2000)) {
		t.Fatal("conteúdo migrado diferente")
	}
	if _, err := a.Ler(r); err == nil {
		t.Fatal("RID antigo deveria estar removido")
	}
	if _, err := a.Atualizar(n, make([]byte, pagina.MaxRegistro+1)); err != ErrGrande {
		t.Fatalf("err = %v", err)
	}
}

func TestVarrer(t *testing.T) {
	a, _ := novo(t)
	var rids []RID
	for i := 0; i < 50; i++ {
		r, _ := a.Inserir(bytes.Repeat([]byte{byte(i)}, 300))
		rids = append(rids, r)
	}
	for i := 0; i < 50; i += 2 {
		a.Remover(rids[i])
	}
	var vistos []byte
	err := a.Varrer(func(_ RID, d []byte) bool { vistos = append(vistos, d[0]); return true })
	if err != nil || len(vistos) != 25 {
		t.Fatalf("visitou %d (%v)", len(vistos), err)
	}
	for _, v := range vistos {
		if v%2 == 0 {
			t.Fatalf("registro removido %d apareceu", v)
		}
	}
	n := 0
	a.Varrer(func(RID, []byte) bool { n++; return n < 5 })
	if n != 5 {
		t.Fatalf("interrupção: %d", n)
	}
}

func TestPersistencia(t *testing.T) {
	a, caminho := novo(t)
	r1, _ := a.Inserir([]byte("um"))
	r2, _ := a.Inserir(bytes.Repeat([]byte("d"), 4000))
	r3, _ := a.Inserir([]byte("tres"))
	a.Remover(r1)
	a.Sincronizar()
	a.Fechar()

	b, err := Abrir(caminho)
	if err != nil {
		t.Fatal(err)
	}
	defer b.Fechar()
	if _, err := b.Ler(r1); err == nil {
		t.Fatal("removido reapareceu")
	}
	if got, _ := b.Ler(r3); string(got) != "tres" {
		t.Fatalf("r3 = %q", got)
	}
	if got, _ := b.Ler(r2); len(got) != 4000 {
		t.Fatal("r2 perdido")
	}
	// espaço livre reconstruído: nova inserção cabe na página 0 ou 1 sem criar demais
	if _, err := b.Inserir([]byte("novo")); err != nil {
		t.Fatal(err)
	}
}

func TestArquivoCorrompido(t *testing.T) {
	prepara := func(t *testing.T) string {
		a, p := novo(t)
		for i := 0; i < 30; i++ {
			a.Inserir(bytes.Repeat([]byte("z"), 300))
		}
		a.Fechar()
		return p
	}
	t.Run("byte invertido", func(t *testing.T) {
		p := prepara(t)
		b, _ := os.ReadFile(p)
		b[pagina.Tamanho+100] ^= 0xFF
		os.WriteFile(p, b, 0o644)
		if _, err := Abrir(p); err == nil {
			t.Fatal("deveria detectar corrupção")
		}
	})
	t.Run("truncado no meio de página", func(t *testing.T) {
		p := prepara(t)
		info, _ := os.Stat(p)
		os.Truncate(p, info.Size()-10)
		if _, err := Abrir(p); err == nil {
			t.Fatal("deveria detectar truncamento")
		}
	})
	t.Run("página inteira cortada abre normalmente", func(t *testing.T) {
		p := prepara(t)
		info, _ := os.Stat(p)
		os.Truncate(p, info.Size()-pagina.Tamanho)
		a, err := Abrir(p)
		if err != nil {
			t.Fatal(err)
		}
		a.Fechar()
	})
}

func TestUsoAposFechar(t *testing.T) {
	a, _ := novo(t)
	a.Fechar()
	if _, err := a.Inserir([]byte("x")); err != ErrFechado {
		t.Fatalf("err = %v", err)
	}
	if _, err := a.Ler(RID{}); err != ErrFechado {
		t.Fatalf("err = %v", err)
	}
	if err := a.Fechar(); err != nil {
		t.Fatal(err)
	}
}

func TestAleatorioContraMapa(t *testing.T) {
	a, _ := novo(t)
	r := rand.New(rand.NewSource(11))
	ref := map[RID][]byte{}
	for i := 0; i < 1500; i++ {
		switch r.Intn(3) {
		case 0:
			d := make([]byte, r.Intn(900))
			r.Read(d)
			rid, err := a.Inserir(d)
			if err != nil {
				t.Fatal(err)
			}
			ref[rid] = d
		case 1:
			for rid := range ref {
				if err := a.Remover(rid); err != nil {
					t.Fatal(err)
				}
				delete(ref, rid)
				break
			}
		default:
			for rid, old := range ref {
				d := make([]byte, r.Intn(1500))
				r.Read(d)
				novo, err := a.Atualizar(rid, d)
				if err != nil {
					t.Fatal(err)
				}
				_ = old
				delete(ref, rid)
				ref[novo] = d
				break
			}
		}
	}
	for rid, d := range ref {
		got, err := a.Ler(rid)
		if err != nil || !bytes.Equal(got, d) {
			t.Fatalf("RID %v divergiu: %v", rid, err)
		}
	}
	n := 0
	a.Varrer(func(RID, []byte) bool { n++; return true })
	if n != len(ref) {
		t.Fatalf("varredura viu %d, esperado %d", n, len(ref))
	}
}

func TestConcorrencia(t *testing.T) {
	a, _ := novo(t)
	var wg sync.WaitGroup
	for g := 0; g < 6; g++ {
		wg.Add(1)
		go func(g int) {
			defer wg.Done()
			for i := 0; i < 60; i++ {
				d := []byte(fmt.Sprintf("g%d-%d", g, i))
				r, err := a.Inserir(d)
				if err != nil {
					t.Error(err)
					return
				}
				if got, err := a.Ler(r); err != nil || !bytes.Equal(got, d) {
					t.Errorf("leitura divergente: %v", err)
				}
			}
		}(g)
	}
	wg.Wait()
	n := 0
	a.Varrer(func(RID, []byte) bool { n++; return true })
	if n != 360 {
		t.Fatalf("registros = %d", n)
	}
}
