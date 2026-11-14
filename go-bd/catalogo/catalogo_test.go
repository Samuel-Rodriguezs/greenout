package catalogo

import (
	"encoding/binary"
	"errors"
	"fmt"
	"hash/crc32"
	"os"
	"path/filepath"
	"reflect"
	"strings"
	"sync"
	"testing"

	"greenout/bd/linhas"
)

func esquema(t *testing.T, cols ...linhas.Coluna) linhas.Esquema {
	t.Helper()
	e, err := linhas.NovoEsquema(cols...)
	if err != nil {
		t.Fatal(err)
	}
	return e
}

func usuarios(t *testing.T) linhas.Esquema {
	return esquema(t,
		linhas.Coluna{Nome: "id", Tipo: linhas.Inteiro},
		linhas.Coluna{Nome: "nome", Tipo: linhas.Texto},
		linhas.Coluna{Nome: "bio", Tipo: linhas.Texto, Nulavel: true},
	)
}

func TestCriarEObter(t *testing.T) {
	c := Novo()
	if err := c.Criar("usuarios", usuarios(t), "id"); err != nil {
		t.Fatal(err)
	}
	tb, ok := c.Obter("usuarios")
	if !ok || tb.Nome != "usuarios" || tb.ChavePrimaria != "id" || len(tb.Esquema.Colunas) != 3 {
		t.Fatalf("tabela = %+v ok=%v", tb, ok)
	}
	if _, ok := c.Obter("outra"); ok {
		t.Fatal("tabela inexistente encontrada")
	}
	if err := c.Criar("usuarios", usuarios(t), ""); !errors.Is(err, ErrExiste) {
		t.Fatalf("duplicada: %v", err)
	}
}

func TestValidacoesDeCriacao(t *testing.T) {
	boa := usuarios(t)
	casos := []struct {
		nome string
		tab  string
		esq  linhas.Esquema
		pk   string
		quer error
	}{
		{"nome vazio", "", boa, "", ErrNome},
		{"nome começa com dígito", "1abc", boa, "", ErrNome},
		{"nome com espaço", "minha tabela", boa, "", ErrNome},
		{"nome com hífen", "a-b", boa, "", ErrNome},
		{"nome longo demais", strings.Repeat("a", 64), boa, "", ErrNome},
		{"esquema vazio", "t", linhas.Esquema{}, "", linhas.ErrEsquema},
		{"coluna com nome inválido", "t", esquema(t, linhas.Coluna{Nome: "a b", Tipo: linhas.Inteiro}), "", ErrNome},
		{"pk inexistente", "t", boa, "zzz", ErrChavePrimaria},
		{"pk nulável", "t", boa, "bio", ErrChavePrimaria},
		{"ok com sublinhado", "_t_1", boa, "id", nil},
	}
	for _, c := range casos {
		t.Run(c.nome, func(t *testing.T) {
			err := Novo().Criar(c.tab, c.esq, c.pk)
			if c.quer == nil && err != nil || c.quer != nil && !errors.Is(err, c.quer) {
				t.Fatalf("err = %v, quer %v", err, c.quer)
			}
		})
	}
}

func TestIsolamentoDeCopias(t *testing.T) {
	c := Novo()
	esq := usuarios(t)
	c.Criar("u", esq, "")
	esq.Colunas[0].Nome = "alterado" // o chamador altera o original
	tb, _ := c.Obter("u")
	if tb.Esquema.Colunas[0].Nome != "id" {
		t.Fatal("catálogo compartilha memória com o esquema do chamador")
	}
	tb.Esquema.Colunas[1].Nome = "outro" // altera a cópia devolvida
	tb2, _ := c.Obter("u")
	if tb2.Esquema.Colunas[1].Nome != "nome" {
		t.Fatal("Obter devolve referência interna")
	}
}

func TestRemoverERenomear(t *testing.T) {
	c := Novo()
	c.Criar("a", usuarios(t), "id")
	c.Criar("b", usuarios(t), "")

	if err := c.Renomear("a", "b"); !errors.Is(err, ErrExiste) {
		t.Fatalf("renomear sobre existente: %v", err)
	}
	if err := c.Renomear("zzz", "c"); !errors.Is(err, ErrNaoExiste) {
		t.Fatalf("renomear inexistente: %v", err)
	}
	if err := c.Renomear("a", "novo nome"); !errors.Is(err, ErrNome) {
		t.Fatalf("nome inválido: %v", err)
	}
	if err := c.Renomear("a", "a"); err != nil {
		t.Fatalf("renomear para si mesma: %v", err)
	}
	if err := c.Renomear("a", "c"); err != nil {
		t.Fatal(err)
	}
	if tb, ok := c.Obter("c"); !ok || tb.Nome != "c" || tb.ChavePrimaria != "id" {
		t.Fatalf("tabela renomeada = %+v", tb)
	}
	if _, ok := c.Obter("a"); ok {
		t.Fatal("nome antigo deveria sumir")
	}
	if err := c.Remover("c"); err != nil {
		t.Fatal(err)
	}
	if err := c.Remover("c"); !errors.Is(err, ErrNaoExiste) {
		t.Fatalf("remover de novo: %v", err)
	}
	if got := c.Listar(); !reflect.DeepEqual(got, []string{"b"}) {
		t.Fatalf("listar = %v", got)
	}
}

func TestAdicionarColuna(t *testing.T) {
	c := Novo()
	c.Criar("u", usuarios(t), "id")
	casos := []struct {
		nome string
		col  linhas.Coluna
		quer error
	}{
		{"obrigatória", linhas.Coluna{Nome: "x", Tipo: linhas.Inteiro}, ErrColunaObrigatoria},
		{"repetida", linhas.Coluna{Nome: "nome", Tipo: linhas.Texto, Nulavel: true}, linhas.ErrEsquema},
		{"nome inválido", linhas.Coluna{Nome: "a b", Tipo: linhas.Texto, Nulavel: true}, ErrNome},
		{"ok", linhas.Coluna{Nome: "idade", Tipo: linhas.Inteiro, Nulavel: true}, nil},
	}
	for _, k := range casos {
		t.Run(k.nome, func(t *testing.T) {
			err := c.AdicionarColuna("u", k.col)
			if k.quer == nil && err != nil || k.quer != nil && !errors.Is(err, k.quer) {
				t.Fatalf("err = %v", err)
			}
		})
	}
	tb, _ := c.Obter("u")
	if len(tb.Esquema.Colunas) != 4 || tb.Esquema.Colunas[3].Nome != "idade" {
		t.Fatalf("colunas = %+v", tb.Esquema.Colunas)
	}
	if err := c.AdicionarColuna("zzz", linhas.Coluna{Nome: "x", Tipo: linhas.Real, Nulavel: true}); !errors.Is(err, ErrNaoExiste) {
		t.Fatalf("tabela inexistente: %v", err)
	}
}

func TestSalvarECarregar(t *testing.T) {
	caminho := filepath.Join(t.TempDir(), "catalogo.db")
	c := Novo()
	c.Criar("usuarios", usuarios(t), "id")
	c.Criar("produtos", esquema(t,
		linhas.Coluna{Nome: "sku", Tipo: linhas.Texto},
		linhas.Coluna{Nome: "preco", Tipo: linhas.Real},
		linhas.Coluna{Nome: "foto", Tipo: linhas.Bytes, Nulavel: true},
		linhas.Coluna{Nome: "ativo", Tipo: linhas.Booleano},
	), "sku")
	if err := c.Salvar(caminho); err != nil {
		t.Fatal(err)
	}
	if _, err := os.Stat(caminho + ".tmp"); !os.IsNotExist(err) {
		t.Fatal("arquivo temporário deveria ter sido renomeado")
	}
	c2, err := Carregar(caminho)
	if err != nil {
		t.Fatal(err)
	}
	if !reflect.DeepEqual(c2.Listar(), c.Listar()) {
		t.Fatalf("tabelas = %v", c2.Listar())
	}
	for _, nome := range c.Listar() {
		a, _ := c.Obter(nome)
		b, _ := c2.Obter(nome)
		if !reflect.DeepEqual(a, b) {
			t.Fatalf("%s diverge:\n%+v\n%+v", nome, a, b)
		}
	}
	// o esquema carregado é utilizável
	tb, _ := c2.Obter("usuarios")
	b, err := tb.Esquema.Codificar([]any{int64(1), "ana", nil})
	if err != nil {
		t.Fatal(err)
	}
	if _, err := tb.Esquema.Decodificar(b); err != nil {
		t.Fatal(err)
	}
}

func TestSalvarSobrescreve(t *testing.T) {
	caminho := filepath.Join(t.TempDir(), "catalogo.db")
	c := Novo()
	c.Criar("a", usuarios(t), "")
	c.Salvar(caminho)
	c.Remover("a")
	c.Criar("b", usuarios(t), "")
	c.Salvar(caminho)
	c2, _ := Carregar(caminho)
	if got := c2.Listar(); !reflect.DeepEqual(got, []string{"b"}) {
		t.Fatalf("tabelas = %v", got)
	}
}

func TestCatalogoVazioPersiste(t *testing.T) {
	caminho := filepath.Join(t.TempDir(), "vazio.db")
	Novo().Salvar(caminho)
	c, err := Carregar(caminho)
	if err != nil || len(c.Listar()) != 0 {
		t.Fatalf("err = %v", err)
	}
}

func TestArquivoCorrompido(t *testing.T) {
	dir := t.TempDir()
	caminho := filepath.Join(dir, "c.db")
	c := Novo()
	c.Criar("usuarios", usuarios(t), "id")
	c.Salvar(caminho)
	bom, _ := os.ReadFile(caminho)

	// grava um arquivo com CRC correto para o corpo dado
	comCRC := func(corpo string) []byte {
		b := append([]byte(magic), 0, 0, 0, 0)
		binary.LittleEndian.PutUint32(b[4:], crc32.ChecksumIEEE([]byte(corpo)))
		return append(b, corpo...)
	}
	casos := []struct {
		nome string
		dado []byte
	}{
		{"vazio", nil},
		{"curto", bom[:5]},
		{"magic errado", append([]byte("XXXX"), bom[4:]...)},
		{"byte do corpo invertido", func() []byte { b := append([]byte(nil), bom...); b[len(b)-3] ^= 1; return b }()},
		{"crc invertido", func() []byte { b := append([]byte(nil), bom...); b[5] ^= 1; return b }()},
		{"truncado", bom[:len(bom)-4]},
		{"json inválido com crc ok", comCRC("{não é json")},
		{"tabela inválida com crc ok", comCRC(`[{"nome":"1ruim","esquema":{"colunas":[{"nome":"a","tipo":"INTEIRO","nulavel":false}]}}]`)},
		{"tipo desconhecido com crc ok", comCRC(`[{"nome":"t","esquema":{"colunas":[{"nome":"a","tipo":"MAGICO","nulavel":false}]}}]`)},
		{"pk inexistente com crc ok", comCRC(`[{"nome":"t","esquema":{"colunas":[{"nome":"a","tipo":"INTEIRO","nulavel":false}]},"chave_primaria":"q"}]`)},
		{"tabela duplicada com crc ok", comCRC(`[{"nome":"t","esquema":{"colunas":[{"nome":"a","tipo":"INTEIRO","nulavel":false}]}},{"nome":"t","esquema":{"colunas":[{"nome":"a","tipo":"INTEIRO","nulavel":false}]}}]`)},
	}
	for _, k := range casos {
		t.Run(k.nome, func(t *testing.T) {
			p := filepath.Join(dir, "x.db")
			os.WriteFile(p, k.dado, 0o644)
			if _, err := Carregar(p); !errors.Is(err, ErrArquivo) && !errors.Is(err, linhas.ErrTipoInvalido) {
				t.Fatalf("err = %v", err)
			}
		})
	}
	if _, err := Carregar(filepath.Join(dir, "nao-existe")); err == nil {
		t.Fatal("arquivo ausente deveria falhar")
	}
}

func TestConcorrencia(t *testing.T) {
	c := Novo()
	esq := usuarios(t)
	var wg sync.WaitGroup
	for g := 0; g < 8; g++ {
		wg.Add(1)
		go func(g int) {
			defer wg.Done()
			for i := 0; i < 50; i++ {
				nome := fmt.Sprintf("t_%d_%d", g, i)
				if err := c.Criar(nome, esq, "id"); err != nil {
					t.Error(err)
					return
				}
				c.Obter(nome)
				c.Listar()
				if i%2 == 0 {
					c.Remover(nome)
				}
			}
		}(g)
	}
	wg.Wait()
	if n := len(c.Listar()); n != 8*25 {
		t.Fatalf("tabelas = %d", n)
	}
}
