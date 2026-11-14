package lsm

import (
	"fmt"
	"math/rand"
	"os"
	"path/filepath"
	"sort"
	"strings"
	"sync"
	"testing"
)

func abrir(t *testing.T, dir string, limite int) *Banco {
	t.Helper()
	b, err := Abrir(dir, Opcoes{LimiteMemtable: limite})
	if err != nil {
		t.Fatal(err)
	}
	t.Cleanup(func() { b.Fechar() })
	return b
}

func esperar(t *testing.T, b *Banco, chave, quer string, existe bool) {
	t.Helper()
	v, ok, err := b.Obter(chave)
	if err != nil {
		t.Fatal(err)
	}
	if ok != existe || string(v) != quer {
		t.Fatalf("Obter(%q) = (%q,%v), quer (%q,%v)", chave, v, ok, quer, existe)
	}
}

func TestMemtable(t *testing.T) {
	casos := []struct {
		nome   string
		passos func(b *Banco)
		chave  string
		quer   string
		existe bool
	}{
		{"ausente", func(*Banco) {}, "a", "", false},
		{"definir", func(b *Banco) { b.Definir("a", []byte("1")) }, "a", "1", true},
		{"sobrescrever", func(b *Banco) { b.Definir("a", []byte("1")); b.Definir("a", []byte("2")) }, "a", "2", true},
		{"remover", func(b *Banco) { b.Definir("a", []byte("1")); b.Remover("a") }, "a", "", false},
		{"valor vazio", func(b *Banco) { b.Definir("a", nil) }, "a", "", true},
		{"chave vazia", func(b *Banco) { b.Definir("", []byte("v")) }, "", "v", true},
	}
	for _, c := range casos {
		t.Run(c.nome, func(t *testing.T) {
			b := abrir(t, t.TempDir(), 0)
			c.passos(b)
			esperar(t, b, c.chave, c.quer, c.existe)
		})
	}
}

func TestFlushAutomaticoELeituraEntreTabelas(t *testing.T) {
	b := abrir(t, t.TempDir(), 300)
	for i := 0; i < 100; i++ {
		b.Definir(fmt.Sprintf("k%03d", i), []byte(fmt.Sprintf("v%d", i)))
	}
	if b.NumTabelas() < 3 {
		t.Fatalf("tabelas = %d, esperava vários flushes", b.NumTabelas())
	}
	for i := 0; i < 100; i++ {
		esperar(t, b, fmt.Sprintf("k%03d", i), fmt.Sprintf("v%d", i), true)
	}
	esperar(t, b, "inexistente", "", false)
	if b.LeiturasEvitadas() == 0 {
		t.Fatal("o filtro de Bloom deveria ter poupado leituras")
	}
}

func TestPrecedenciaEntreTabelas(t *testing.T) {
	b := abrir(t, t.TempDir(), 0)
	b.Definir("a", []byte("v1"))
	b.Definir("b", []byte("b1"))
	b.Descarregar()
	b.Definir("a", []byte("v2"))
	b.Remover("b")
	b.Descarregar()
	b.Definir("a", []byte("v3"))
	esperar(t, b, "a", "v3", true)
	b.Descarregar()
	esperar(t, b, "a", "v3", true)
	esperar(t, b, "b", "", false)
	if b.NumTabelas() != 3 {
		t.Fatalf("tabelas = %d", b.NumTabelas())
	}
}

func TestPersistenciaEReabertura(t *testing.T) {
	dir := t.TempDir()
	b, _ := Abrir(dir, Opcoes{LimiteMemtable: 200})
	for i := 0; i < 50; i++ {
		b.Definir(fmt.Sprintf("k%02d", i), []byte("x"))
	}
	b.Remover("k10")
	if err := b.Fechar(); err != nil {
		t.Fatal(err)
	}
	if _, _, err := b.Obter("k01"); err != ErrFechado {
		t.Fatalf("após fechar: %v", err)
	}
	b2 := abrir(t, dir, 200)
	esperar(t, b2, "k01", "x", true)
	esperar(t, b2, "k10", "", false)
	b2.Definir("novo", []byte("n"))
	b2.Descarregar()
	esperar(t, b2, "novo", "n", true)
}

func TestIntervalo(t *testing.T) {
	b := abrir(t, t.TempDir(), 0)
	for _, k := range []string{"a", "b", "c", "d", "e"} {
		b.Definir(k, []byte(strings.ToUpper(k)))
	}
	b.Descarregar()
	b.Definir("c", []byte("novo"))
	b.Remover("d")
	b.Definir("f", []byte("F"))

	casos := []struct {
		nome    string
		de, ate string
		quer    string
	}{
		{"tudo", "", "", "a=A b=B c=novo e=E f=F"},
		{"meio", "b", "e", "b=B c=novo"},
		{"sem limite superior", "c", "", "c=novo e=E f=F"},
		{"vazio", "x", "z", ""},
	}
	for _, c := range casos {
		t.Run(c.nome, func(t *testing.T) {
			es, err := b.Intervalo(c.de, c.ate)
			if err != nil {
				t.Fatal(err)
			}
			var partes []string
			for _, e := range es {
				partes = append(partes, e.Chave+"="+string(e.Valor))
			}
			if got := strings.Join(partes, " "); got != c.quer {
				t.Fatalf("got %q, quer %q", got, c.quer)
			}
		})
	}
}

func TestCompactacao(t *testing.T) {
	dir := t.TempDir()
	b := abrir(t, dir, 0)
	ref := map[string]string{}
	r := rand.New(rand.NewSource(4))
	for rodada := 0; rodada < 6; rodada++ {
		for i := 0; i < 40; i++ {
			k := fmt.Sprintf("k%02d", r.Intn(30))
			if r.Intn(4) == 0 {
				b.Remover(k)
				delete(ref, k)
			} else {
				v := fmt.Sprintf("r%d-%d", rodada, i)
				b.Definir(k, []byte(v))
				ref[k] = v
			}
		}
		b.Descarregar()
	}
	if b.NumTabelas() != 6 {
		t.Fatalf("tabelas = %d", b.NumTabelas())
	}
	if err := b.Compactar(); err != nil {
		t.Fatal(err)
	}
	if b.NumTabelas() != 1 {
		t.Fatalf("depois de compactar: %d tabelas", b.NumTabelas())
	}
	arquivos, _ := filepath.Glob(filepath.Join(dir, "*.sst"))
	if len(arquivos) != 1 {
		t.Fatalf("arquivos no disco = %v", arquivos)
	}
	for k := 0; k < 30; k++ {
		chave := fmt.Sprintf("k%02d", k)
		v, existe := ref[chave]
		esperar(t, b, chave, v, existe)
	}
	// sem lápides na tabela compactada: todas as entradas são vivas
	es, _ := b.tabelas[0].todas()
	if len(es) != len(ref) {
		t.Fatalf("tabela compactada tem %d entradas, quer %d", len(es), len(ref))
	}
	for _, e := range es {
		if e.Apagado {
			t.Fatal("lápide sobreviveu à compactação")
		}
	}
	// reabrir mantém o resultado e novos flushes entram por cima
	b.Fechar()
	b2 := abrir(t, dir, 0)
	b2.Definir("k00", []byte("depois"))
	b2.Descarregar()
	esperar(t, b2, "k00", "depois", true)
	if err := b2.Compactar(); err != nil {
		t.Fatal(err)
	}
	esperar(t, b2, "k00", "depois", true)
}

func TestCompactarTudoRemovido(t *testing.T) {
	b := abrir(t, t.TempDir(), 0)
	b.Definir("a", []byte("1"))
	b.Descarregar()
	b.Remover("a")
	b.Descarregar()
	if err := b.Compactar(); err != nil {
		t.Fatal(err)
	}
	esperar(t, b, "a", "", false)
	es, _ := b.Intervalo("", "")
	if len(es) != 0 {
		t.Fatalf("restou %v", es)
	}
}

func TestQuedaNaCompactacaoNaoRessuscitaDados(t *testing.T) {
	dir := t.TempDir()
	b, _ := Abrir(dir, Opcoes{})
	b.Definir("a", []byte("antigo"))
	b.Descarregar()
	b.Remover("a")
	b.Descarregar()
	// simula a queda: guarda cópias das tabelas antigas, compacta e as devolve
	copias := map[string][]byte{}
	for _, t := range b.tabelas {
		d, _ := os.ReadFile(t.caminho)
		copias[filepath.Base(t.caminho)] = d
	}
	b.Compactar()
	b.Fechar()
	for nome, d := range copias {
		os.WriteFile(filepath.Join(dir, nome), d, 0o644)
	}
	b2 := abrir(t, dir, 0)
	esperar(t, b2, "a", "", false)
	if b2.NumTabelas() != 1 {
		t.Fatalf("tabelas = %d, as antigas deveriam ter sido descartadas", b2.NumTabelas())
	}
}

func TestArquivoTmpResidualEIgnorado(t *testing.T) {
	dir := t.TempDir()
	b, _ := Abrir(dir, Opcoes{})
	b.Definir("a", []byte("1"))
	b.Fechar()
	os.WriteFile(filepath.Join(dir, "00000009.sst.tmp"), []byte("lixo"), 0o644)
	b2 := abrir(t, dir, 0)
	esperar(t, b2, "a", "1", true)
	if _, err := os.Stat(filepath.Join(dir, "00000009.sst.tmp")); !os.IsNotExist(err) {
		t.Fatal("tmp residual deveria ser removido")
	}
}

func TestSSTableCorrompida(t *testing.T) {
	prepara := func(t *testing.T) (string, string) {
		dir := t.TempDir()
		b, _ := Abrir(dir, Opcoes{})
		for i := 0; i < 20; i++ {
			b.Definir(fmt.Sprintf("k%02d", i), []byte("valor"))
		}
		b.Fechar()
		arqs, _ := filepath.Glob(filepath.Join(dir, "*.sst"))
		return dir, arqs[0]
	}
	casos := []struct {
		nome string
		muda func(caminho string)
	}{
		{"byte dos dados invertido", func(p string) { b, _ := os.ReadFile(p); b[10] ^= 0xFF; os.WriteFile(p, b, 0o644) }},
		{"byte do bloom invertido", func(p string) { b, _ := os.ReadFile(p); b[len(b)-tamRodape-5] ^= 1; os.WriteFile(p, b, 0o644) }},
		{"magic alterado", func(p string) { b, _ := os.ReadFile(p); b[len(b)-1] ^= 1; os.WriteFile(p, b, 0o644) }},
		{"truncada no meio", func(p string) { b, _ := os.ReadFile(p); os.WriteFile(p, b[:len(b)/2], 0o644) }},
		{"truncada no rodapé", func(p string) { b, _ := os.ReadFile(p); os.WriteFile(p, b[:len(b)-3], 0o644) }},
		{"vazia", func(p string) { os.WriteFile(p, nil, 0o644) }},
	}
	for _, c := range casos {
		t.Run(c.nome, func(t *testing.T) {
			dir, arq := prepara(t)
			c.muda(arq)
			if _, err := Abrir(dir, Opcoes{}); err == nil {
				t.Fatal("deveria detectar a corrupção")
			}
		})
	}
}

func TestNomeInesperado(t *testing.T) {
	dir := t.TempDir()
	os.WriteFile(filepath.Join(dir, "abc.sst"), nil, 0o644)
	if _, err := Abrir(dir, Opcoes{}); err == nil {
		t.Fatal("nome inválido deveria falhar")
	}
	dir2 := t.TempDir()
	os.WriteFile(filepath.Join(dir2, "leia-me.txt"), []byte("x"), 0o644)
	b, err := Abrir(dir2, Opcoes{})
	if err != nil {
		t.Fatalf("arquivos alheios devem ser ignorados: %v", err)
	}
	b.Fechar()
}

func TestAleatorioContraMapa(t *testing.T) {
	b := abrir(t, t.TempDir(), 400)
	r := rand.New(rand.NewSource(21))
	ref := map[string]string{}
	for i := 0; i < 3000; i++ {
		k := fmt.Sprintf("k%03d", r.Intn(150))
		switch r.Intn(10) {
		case 0, 1, 2:
			b.Remover(k)
			delete(ref, k)
		case 3:
			if i%97 == 0 {
				if err := b.Compactar(); err != nil {
					t.Fatal(err)
				}
			}
		default:
			v := fmt.Sprint("v", i)
			b.Definir(k, []byte(v))
			ref[k] = v
		}
	}
	for k := 0; k < 150; k++ {
		chave := fmt.Sprintf("k%03d", k)
		v, existe := ref[chave]
		esperar(t, b, chave, v, existe)
	}
	es, err := b.Intervalo("", "")
	if err != nil {
		t.Fatal(err)
	}
	var quer []string
	for k := range ref {
		quer = append(quer, k)
	}
	sort.Strings(quer)
	if len(es) != len(quer) {
		t.Fatalf("intervalo com %d entradas, quer %d", len(es), len(quer))
	}
	for i, e := range es {
		if e.Chave != quer[i] || string(e.Valor) != ref[e.Chave] {
			t.Fatalf("entrada %d diverge: %s", i, e.Chave)
		}
	}
}

func TestValoresBinarios(t *testing.T) {
	b := abrir(t, t.TempDir(), 0)
	bin := []byte{0, 1, 2, 255, 0, 10, 13}
	b.Definir("bin\x00chave", bin)
	b.Descarregar()
	v, ok, _ := b.Obter("bin\x00chave")
	if !ok || string(v) != string(bin) {
		t.Fatalf("valor binário = %v", v)
	}
	// o retorno é cópia
	v[0] = 99
	v2, _, _ := b.Obter("bin\x00chave")
	if v2[0] != 0 {
		t.Fatal("Obter deve devolver cópia")
	}
}

func TestConcorrencia(t *testing.T) {
	b := abrir(t, t.TempDir(), 500)
	var wg sync.WaitGroup
	for g := 0; g < 6; g++ {
		wg.Add(1)
		go func(g int) {
			defer wg.Done()
			for i := 0; i < 150; i++ {
				k := fmt.Sprintf("g%d-%03d", g, i)
				if err := b.Definir(k, []byte(k)); err != nil {
					t.Error(err)
					return
				}
				if v, ok, err := b.Obter(k); err != nil || !ok || string(v) != k {
					t.Errorf("leitura de %s: %v %v", k, ok, err)
					return
				}
				if i%50 == 0 {
					if _, err := b.Intervalo("g", "h"); err != nil {
						t.Error(err)
					}
				}
			}
		}(g)
	}
	wg.Wait()
	if err := b.Compactar(); err != nil {
		t.Fatal(err)
	}
	es, _ := b.Intervalo("", "")
	if len(es) != 900 {
		t.Fatalf("entradas = %d", len(es))
	}
}
