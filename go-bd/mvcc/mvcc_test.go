package mvcc

import (
	"fmt"
	"strconv"
	"sync"
	"testing"
)

func ler(t *testing.T, tx *Tx, k string) (string, bool) {
	t.Helper()
	v, ok, err := tx.Obter(k)
	if err != nil {
		t.Fatal(err)
	}
	return string(v), ok
}

func confirmar(t *testing.T, b *Banco, pares ...string) {
	t.Helper()
	tx := b.Comecar()
	for i := 0; i+1 < len(pares); i += 2 {
		tx.Definir(pares[i], []byte(pares[i+1]))
	}
	if err := tx.Commit(); err != nil {
		t.Fatal(err)
	}
}

func TestLeituraDeSnapshot(t *testing.T) {
	b := Novo()
	confirmar(t, b, "x", "1")
	leitor := b.Comecar()
	confirmar(t, b, "x", "2", "y", "novo")

	if v, _ := ler(t, leitor, "x"); v != "1" {
		t.Fatalf("leitura repetível: x = %q", v)
	}
	if _, ok := ler(t, leitor, "y"); ok {
		t.Fatal("snapshot não deve ver chave confirmada depois")
	}
	novo := b.Comecar()
	if v, _ := ler(t, novo, "x"); v != "2" {
		t.Fatalf("nova transação deveria ver x=2, viu %q", v)
	}
}

func TestSemLeituraSuja(t *testing.T) {
	b := Novo()
	a, c := b.Comecar(), b.Comecar()
	a.Definir("k", []byte("rascunho"))
	if _, ok := ler(t, c, "k"); ok {
		t.Fatal("leitura suja")
	}
	if v, ok := ler(t, a, "k"); !ok || v != "rascunho" {
		t.Fatal("a transação deve ver as próprias escritas")
	}
	a.Abortar()
	if _, ok := ler(t, b.Comecar(), "k"); ok {
		t.Fatal("escrita abortada apareceu")
	}
}

func TestRemocaoESobrescrita(t *testing.T) {
	b := Novo()
	confirmar(t, b, "k", "v")
	tx := b.Comecar()
	tx.Remover("k")
	if _, ok := ler(t, tx, "k"); ok {
		t.Fatal("remoção local deveria esconder a chave")
	}
	antes := b.Comecar()
	tx.Commit()
	if v, ok := ler(t, antes, "k"); !ok || v != "v" {
		t.Fatal("snapshot anterior deveria ainda ver o valor")
	}
	if _, ok := ler(t, b.Comecar(), "k"); ok {
		t.Fatal("chave removida ainda visível")
	}
	// ressuscitar
	confirmar(t, b, "k", "de volta")
	if v, _ := ler(t, b.Comecar(), "k"); v != "de volta" {
		t.Fatalf("v = %q", v)
	}
}

func TestConflitoPrimeiroCommitVence(t *testing.T) {
	b := Novo()
	confirmar(t, b, "k", "0")
	t1, t2 := b.Comecar(), b.Comecar()
	t1.Definir("k", []byte("1"))
	t2.Definir("k", []byte("2"))
	if err := t1.Commit(); err != nil {
		t.Fatal(err)
	}
	if err := t2.Commit(); err != ErrConflito {
		t.Fatalf("err = %v", err)
	}
	if v, _ := ler(t, b.Comecar(), "k"); v != "1" {
		t.Fatalf("k = %q", v)
	}
	if _, _, err := t2.Obter("k"); err != ErrFinalizada {
		t.Fatalf("transação com conflito deve ficar finalizada: %v", err)
	}
}

func TestEscritasEmChavesDiferentesNaoConflitam(t *testing.T) {
	b := Novo()
	t1, t2 := b.Comecar(), b.Comecar()
	t1.Definir("a", []byte("1"))
	t2.Definir("b", []byte("2"))
	if t1.Commit() != nil || t2.Commit() != nil {
		t.Fatal("não deveria haver conflito")
	}
}

func TestWriteSkewEPermitido(t *testing.T) {
	// duas transações leem a mesma regra ("pelo menos um de plantão") e
	// escrevem chaves distintas: snapshot isolation deixa ambas confirmarem
	b := Novo()
	confirmar(t, b, "ana", "plantao", "bia", "plantao")
	t1, t2 := b.Comecar(), b.Comecar()
	for _, tx := range []*Tx{t1, t2} {
		ler(t, tx, "ana")
		ler(t, tx, "bia")
	}
	t1.Definir("ana", []byte("folga"))
	t2.Definir("bia", []byte("folga"))
	if t1.Commit() != nil || t2.Commit() != nil {
		t.Fatal("write skew deveria ser aceito sob snapshot isolation")
	}
	final := b.Comecar()
	a, _ := ler(t, final, "ana")
	bi, _ := ler(t, final, "bia")
	if a != "folga" || bi != "folga" {
		t.Fatalf("ana=%s bia=%s", a, bi)
	}
}

func TestTransacaoSomenteLeituraNuncaConflita(t *testing.T) {
	b := Novo()
	confirmar(t, b, "k", "1")
	r := b.Comecar()
	confirmar(t, b, "k", "2")
	ler(t, r, "k")
	if err := r.Commit(); err != nil {
		t.Fatal(err)
	}
}

func TestUsoAposFim(t *testing.T) {
	b := Novo()
	tx := b.Comecar()
	tx.Commit()
	if err := tx.Definir("a", nil); err != ErrFinalizada {
		t.Fatalf("definir: %v", err)
	}
	if err := tx.Remover("a"); err != ErrFinalizada {
		t.Fatalf("remover: %v", err)
	}
	if err := tx.Commit(); err != ErrFinalizada {
		t.Fatalf("commit: %v", err)
	}
	tx.Abortar() // inofensivo
}

func TestValorEhCopiado(t *testing.T) {
	b := Novo()
	tx := b.Comecar()
	buf := []byte("abc")
	tx.Definir("k", buf)
	buf[0] = 'X'
	tx.Commit()
	v, _, _ := b.Comecar().Obter("k")
	if string(v) != "abc" {
		t.Fatalf("v = %q", v)
	}
	v[0] = 'Z'
	v2, _, _ := b.Comecar().Obter("k")
	if string(v2) != "abc" {
		t.Fatal("alterar o retorno não pode afetar o banco")
	}
}

func TestPodar(t *testing.T) {
	b := Novo()
	for i := 0; i < 5; i++ {
		confirmar(t, b, "k", strconv.Itoa(i))
	}
	leitor := b.Comecar() // enxerga k=4
	for i := 5; i < 8; i++ {
		confirmar(t, b, "k", strconv.Itoa(i))
	}
	if b.NumVersoes() != 8 {
		t.Fatalf("versões = %d", b.NumVersoes())
	}
	if n := b.Podar(); n != 4 {
		t.Fatalf("podou %d, quer 4 (versões 0..3)", n)
	}
	if v, _ := ler(t, leitor, "k"); v != "4" {
		t.Fatalf("leitor perdeu a versão: %q", v)
	}
	leitor.Commit()
	if n := b.Podar(); n != 3 {
		t.Fatalf("podou %d, quer 3", n)
	}
	if b.NumVersoes() != 1 {
		t.Fatalf("versões = %d", b.NumVersoes())
	}
	// chave removida e sem leitores antigos some por completo
	tx := b.Comecar()
	tx.Remover("k")
	tx.Commit()
	b.Podar()
	if b.NumVersoes() != 0 {
		t.Fatalf("versões = %d", b.NumVersoes())
	}
}

func TestContadorConcorrenteComRetentativa(t *testing.T) {
	b := Novo()
	confirmar(t, b, "contador", "0")
	const goroutines, incrementos = 8, 50
	var wg sync.WaitGroup
	var conflitos int
	var mu sync.Mutex
	for g := 0; g < goroutines; g++ {
		wg.Add(1)
		go func() {
			defer wg.Done()
			for i := 0; i < incrementos; i++ {
				for {
					tx := b.Comecar()
					v, _, _ := tx.Obter("contador")
					n, _ := strconv.Atoi(string(v))
					tx.Definir("contador", []byte(strconv.Itoa(n+1)))
					err := tx.Commit()
					if err == nil {
						break
					}
					if err != ErrConflito {
						t.Error(err)
						return
					}
					mu.Lock()
					conflitos++
					mu.Unlock()
				}
			}
		}()
	}
	wg.Wait()
	v, _, _ := b.Comecar().Obter("contador")
	if string(v) != strconv.Itoa(goroutines*incrementos) {
		t.Fatalf("contador = %s, quer %d (conflitos=%d)", v, goroutines*incrementos, conflitos)
	}
}

func TestTransferenciasEFotografiasConsistentes(t *testing.T) {
	const contas, saldo = 6, 100
	b := Novo()
	ini := b.Comecar()
	for i := 0; i < contas; i++ {
		ini.Definir(fmt.Sprint("c", i), []byte(strconv.Itoa(saldo)))
	}
	ini.Commit()

	var wg sync.WaitGroup
	parar := make(chan struct{})
	// leitores: toda fotografia deve somar o total
	for r := 0; r < 3; r++ {
		wg.Add(1)
		go func() {
			defer wg.Done()
			for {
				select {
				case <-parar:
					return
				default:
				}
				tx := b.Comecar()
				soma := 0
				for i := 0; i < contas; i++ {
					v, _, _ := tx.Obter(fmt.Sprint("c", i))
					n, _ := strconv.Atoi(string(v))
					soma += n
				}
				tx.Commit()
				if soma != contas*saldo {
					t.Errorf("fotografia inconsistente: soma = %d", soma)
					return
				}
			}
		}()
	}
	var escritores sync.WaitGroup
	for w := 0; w < 4; w++ {
		escritores.Add(1)
		go func(w int) {
			defer escritores.Done()
			for i := 0; i < 100; i++ {
				de, para := fmt.Sprint("c", (w+i)%contas), fmt.Sprint("c", (w+i+1)%contas)
				for {
					tx := b.Comecar()
					a, _, _ := tx.Obter(de)
					c, _, _ := tx.Obter(para)
					na, _ := strconv.Atoi(string(a))
					nc, _ := strconv.Atoi(string(c))
					tx.Definir(de, []byte(strconv.Itoa(na-1)))
					tx.Definir(para, []byte(strconv.Itoa(nc+1)))
					if tx.Commit() == nil {
						break
					}
				}
			}
		}(w)
	}
	escritores.Wait()
	close(parar)
	wg.Wait()
}
