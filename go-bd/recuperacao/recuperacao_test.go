package recuperacao

import (
	"fmt"
	"os"
	"path/filepath"
	"sync"
	"testing"

	"greenout/bd/wal"
)

func preparar(t *testing.T) string {
	t.Helper()
	p := filepath.Join(t.TempDir(), "banco.wal")
	b, _, err := Abrir(p)
	if err != nil {
		t.Fatal(err)
	}
	b.Definir("a", "1")
	b.Definir("b", "2")
	b.Definir("a", "3")
	b.Remover("b")
	b.Definir("c", "ultimo")
	b.Fechar()
	return p
}

func TestReabrirSemFalha(t *testing.T) {
	p := preparar(t)
	b, rel, err := Abrir(p)
	if err != nil {
		t.Fatal(err)
	}
	defer b.Fechar()
	if rel.Reproduzidos != 5 || rel.Anomalia != nil || rel.BytesPerdidos != 0 {
		t.Fatalf("relatório = %+v", rel)
	}
	if v, _ := b.Obter("a"); v != "3" {
		t.Fatalf("a = %q", v)
	}
	if _, ok := b.Obter("b"); ok {
		t.Fatal("b deveria ter sido removida")
	}
	if b.Tamanho() != 2 {
		t.Fatalf("tamanho = %d", b.Tamanho())
	}
}

func TestQuedaTruncandoFinal(t *testing.T) {
	for corte := int64(1); corte <= 6; corte++ {
		t.Run(fmt.Sprintf("corta %d bytes", corte), func(t *testing.T) {
			p := preparar(t)
			info, _ := os.Stat(p)
			if err := os.Truncate(p, info.Size()-corte); err != nil {
				t.Fatal(err)
			}
			b, rel, err := Abrir(p)
			if err != nil {
				t.Fatal(err)
			}
			if rel.Reproduzidos != 4 || rel.Anomalia != wal.ErrTruncado || rel.BytesPerdidos == 0 {
				t.Fatalf("relatório = %+v", rel)
			}
			if _, ok := b.Obter("c"); ok {
				t.Fatal("última operação deveria ter sido perdida")
			}
			if v, _ := b.Obter("a"); v != "3" {
				t.Fatalf("a = %q", v)
			}
			// o log foi aparado: novas escritas devem sobreviver a outra reabertura
			if err := b.Definir("novo", "v"); err != nil {
				t.Fatal(err)
			}
			b.Fechar()
			b2, rel2, err := Abrir(p)
			if err != nil || rel2.Anomalia != nil {
				t.Fatalf("segunda abertura: %v %+v", err, rel2)
			}
			defer b2.Fechar()
			if v, ok := b2.Obter("novo"); !ok || v != "v" {
				t.Fatal("escrita pós-recuperação perdida")
			}
		})
	}
}

func TestCorrupcaoNoMeio(t *testing.T) {
	p := preparar(t)
	dados, _ := os.ReadFile(p)
	// o 1º registro (SET a 1) ocupa 8 de cabeçalho + 5 de carga = 13 bytes;
	// corrompe um byte da carga do 2º registro
	dados[13+9] ^= 0xFF
	os.WriteFile(p, dados, 0o644)
	b, rel, err := Abrir(p)
	if err != nil {
		t.Fatal(err)
	}
	defer b.Fechar()
	if rel.Reproduzidos != 1 || rel.Anomalia != wal.ErrCorrompido {
		t.Fatalf("relatório = %+v", rel)
	}
	if b.Tamanho() != 1 {
		t.Fatalf("tamanho = %d", b.Tamanho())
	}
}

func TestArquivoInexistenteCriaBanco(t *testing.T) {
	b, rel, err := Abrir(filepath.Join(t.TempDir(), "novo.wal"))
	if err != nil {
		t.Fatal(err)
	}
	defer b.Fechar()
	if rel.Reproduzidos != 0 || b.Tamanho() != 0 {
		t.Fatalf("relatório = %+v", rel)
	}
}

func TestRegistroComFormatoInvalido(t *testing.T) {
	casos := []struct {
		nome  string
		carga []byte
	}{
		{"vazio", []byte{}},
		{"op desconhecida", []byte{9, 1, 'a'}},
		{"chave além do fim", []byte{opRemover, 10, 'a'}},
		{"sem valor", []byte{opDefinir, 1, 'a'}},
		{"bytes sobrando", []byte{opRemover, 1, 'a', 0}},
	}
	for _, c := range casos {
		t.Run(c.nome, func(t *testing.T) {
			p := filepath.Join(t.TempDir(), "x.wal")
			l, _ := wal.Abrir(p)
			l.Anexar(c.carga)
			l.Fechar()
			if _, _, err := Abrir(p); err != ErrRegistroInvalido {
				t.Fatalf("err = %v", err)
			}
		})
	}
}

func TestValoresEspeciais(t *testing.T) {
	p := filepath.Join(t.TempDir(), "x.wal")
	b, _, _ := Abrir(p)
	b.Definir("", "")
	b.Definir("chave\x00bin", "valor com\nquebra e ç")
	b.Fechar()
	b, _, err := Abrir(p)
	if err != nil {
		t.Fatal(err)
	}
	defer b.Fechar()
	if v, ok := b.Obter(""); !ok || v != "" {
		t.Fatal("chave vazia perdida")
	}
	if v, _ := b.Obter("chave\x00bin"); v != "valor com\nquebra e ç" {
		t.Fatalf("valor = %q", v)
	}
}

func TestEscritaConcorrente(t *testing.T) {
	p := filepath.Join(t.TempDir(), "c.wal")
	b, _, _ := Abrir(p)
	var wg sync.WaitGroup
	for g := 0; g < 6; g++ {
		wg.Add(1)
		go func(g int) {
			defer wg.Done()
			for i := 0; i < 100; i++ {
				b.Definir(fmt.Sprintf("%d-%d", g, i), "v")
				b.Obter("0-0")
			}
		}(g)
	}
	wg.Wait()
	b.Fechar()
	b2, rel, err := Abrir(p)
	if err != nil || rel.Reproduzidos != 600 || b2.Tamanho() != 600 {
		t.Fatalf("err=%v rel=%+v", err, rel)
	}
	b2.Fechar()
}
