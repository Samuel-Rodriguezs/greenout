package wal

import (
	"bytes"
	"fmt"
	"os"
	"path/filepath"
	"sync"
	"testing"
)

func coletar(t *testing.T, caminho string) ([][]byte, Resultado) {
	t.Helper()
	var regs [][]byte
	res, err := Reproduzir(caminho, func(c []byte) error {
		regs = append(regs, append([]byte(nil), c...))
		return nil
	})
	if err != nil {
		t.Fatal(err)
	}
	return regs, res
}

func escrever(t *testing.T, p string, cargas ...[]byte) {
	t.Helper()
	l, err := Abrir(p)
	if err != nil {
		t.Fatal(err)
	}
	for _, c := range cargas {
		if err := l.Anexar(c); err != nil {
			t.Fatal(err)
		}
	}
	if err := l.Fechar(); err != nil {
		t.Fatal(err)
	}
}

func TestAnexarEReproduzir(t *testing.T) {
	casos := []struct {
		nome   string
		cargas [][]byte
	}{
		{"vazio", nil},
		{"um", [][]byte{[]byte("ola")}},
		{"carga vazia", [][]byte{{}, []byte("x"), {}}},
		{"varios", [][]byte{[]byte("a"), []byte("bb"), bytes.Repeat([]byte("z"), 10000)}},
	}
	for _, c := range casos {
		t.Run(c.nome, func(t *testing.T) {
			p := filepath.Join(t.TempDir(), "log")
			escrever(t, p, c.cargas...)
			regs, res := coletar(t, p)
			if res.Anomalia != nil || res.Registros != len(c.cargas) || res.OffsetValido != res.Tamanho {
				t.Fatalf("resultado inesperado: %+v", res)
			}
			for i := range c.cargas {
				if !bytes.Equal(regs[i], c.cargas[i]) {
					t.Fatalf("registro %d diferente", i)
				}
			}
		})
	}
}

func TestSincronizar(t *testing.T) {
	l, _ := Abrir(filepath.Join(t.TempDir(), "log"))
	defer l.Fechar()
	l.Anexar([]byte("a"))
	if err := l.Sincronizar(); err != nil {
		t.Fatal(err)
	}
}

func TestReaberturaAnexaNoFim(t *testing.T) {
	p := filepath.Join(t.TempDir(), "log")
	for i := 0; i < 3; i++ {
		escrever(t, p, []byte(fmt.Sprint("r", i)))
	}
	regs, res := coletar(t, p)
	if len(regs) != 3 || res.Anomalia != nil {
		t.Fatalf("regs=%d res=%+v", len(regs), res)
	}
}

func TestTruncamento(t *testing.T) {
	primeiro := int64(cabecalho + len("primeiro"))
	total := primeiro + int64(cabecalho+len("segundo"))

	// corta de 1 byte até remover todo o segundo registro
	for corte := int64(1); corte <= total-primeiro; corte++ {
		p := filepath.Join(t.TempDir(), "log")
		escrever(t, p, []byte("primeiro"), []byte("segundo"))
		if err := os.Truncate(p, total-corte); err != nil {
			t.Fatal(err)
		}
		regs, res := coletar(t, p)
		if len(regs) != 1 || res.OffsetValido != primeiro {
			t.Fatalf("corte %d: regs=%d off=%d", corte, len(regs), res.OffsetValido)
		}
		limpo := total-corte == primeiro
		if limpo && res.Anomalia != nil {
			t.Fatalf("corte %d: anomalia inesperada %v", corte, res.Anomalia)
		}
		if !limpo && res.Anomalia != ErrTruncado {
			t.Fatalf("corte %d: anomalia = %v", corte, res.Anomalia)
		}
	}
}

func TestCorrupcao(t *testing.T) {
	casos := []struct {
		nome    string
		posicao func(tam int) int
		quer    int // registros válidos esperados
	}{
		{"byte da carga do primeiro", func(int) int { return cabecalho + 1 }, 0},
		{"checksum do primeiro", func(int) int { return 5 }, 0},
		{"ultimo byte", func(tam int) int { return tam - 1 }, 1},
	}
	for _, c := range casos {
		t.Run(c.nome, func(t *testing.T) {
			p := filepath.Join(t.TempDir(), "log")
			escrever(t, p, []byte("primeiro"), []byte("segundo"))
			b, _ := os.ReadFile(p)
			b[c.posicao(len(b))] ^= 0xFF
			os.WriteFile(p, b, 0o644)
			_, res := coletar(t, p)
			if res.Anomalia != ErrCorrompido || res.Registros != c.quer {
				t.Fatalf("res = %+v", res)
			}
		})
	}
}

func TestTamanhoAbsurdo(t *testing.T) {
	p := filepath.Join(t.TempDir(), "log")
	b := make([]byte, cabecalho)
	b[0], b[1], b[2], b[3] = 0xFF, 0xFF, 0xFF, 0xFF
	os.WriteFile(p, b, 0o644)
	_, res := coletar(t, p)
	if res.Anomalia != ErrCorrompido || res.Registros != 0 {
		t.Fatalf("res = %+v", res)
	}
}

func TestErroDaCallback(t *testing.T) {
	p := filepath.Join(t.TempDir(), "log")
	escrever(t, p, []byte("a"))
	quer := fmt.Errorf("falha")
	_, err := Reproduzir(p, func([]byte) error { return quer })
	if err != quer {
		t.Fatalf("err = %v", err)
	}
}

func TestUsoAposFechar(t *testing.T) {
	l, _ := Abrir(filepath.Join(t.TempDir(), "log"))
	l.Fechar()
	if err := l.Anexar([]byte("x")); err != ErrFechado {
		t.Fatalf("err = %v", err)
	}
	if err := l.Sincronizar(); err != ErrFechado {
		t.Fatalf("sync err = %v", err)
	}
	if err := l.Fechar(); err != nil {
		t.Fatalf("fechar duas vezes: %v", err)
	}
	if _, err := Reproduzir(filepath.Join(t.TempDir(), "naoexiste"), nil); err == nil {
		t.Fatal("deveria falhar para arquivo ausente")
	}
}

func TestCargaGrande(t *testing.T) {
	l, _ := Abrir(filepath.Join(t.TempDir(), "log"))
	defer l.Fechar()
	if err := l.Anexar(make([]byte, TamanhoMaximo+1)); err != ErrGrande {
		t.Fatalf("err = %v", err)
	}
}

func TestAnexoConcorrente(t *testing.T) {
	p := filepath.Join(t.TempDir(), "log")
	l, _ := Abrir(p)
	var wg sync.WaitGroup
	for g := 0; g < 8; g++ {
		wg.Add(1)
		go func(g int) {
			defer wg.Done()
			for i := 0; i < 100; i++ {
				if err := l.Anexar([]byte(fmt.Sprintf("g%d-%d", g, i))); err != nil {
					t.Error(err)
				}
			}
		}(g)
	}
	wg.Wait()
	l.Fechar()
	regs, res := coletar(t, p)
	if len(regs) != 800 || res.Anomalia != nil {
		t.Fatalf("regs=%d res=%+v", len(regs), res)
	}
}
