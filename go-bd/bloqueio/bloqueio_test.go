package bloqueio

import (
	"context"
	"errors"
	"math/rand"
	"sync"
	"testing"
	"time"
)

var bg = context.Background()

// aguardar espera (com limite de tempo) a transação entrar em espera.
func aguardar(t *testing.T, g *Gerente, tx TxID) {
	t.Helper()
	limite := time.Now().Add(5 * time.Second)
	for !g.Esperando(tx) {
		if time.Now().After(limite) {
			t.Fatalf("tx %d nunca entrou em espera", tx)
		}
		time.Sleep(time.Millisecond)
	}
}

func TestCompatibilidade(t *testing.T) {
	casos := []struct {
		nome     string
		a, b     Modo
		bloqueia bool
	}{
		{"S com S", Compartilhado, Compartilhado, false},
		{"S com X", Compartilhado, Exclusivo, true},
		{"X com S", Exclusivo, Compartilhado, true},
		{"X com X", Exclusivo, Exclusivo, true},
	}
	for _, c := range casos {
		t.Run(c.nome, func(t *testing.T) {
			g := Novo()
			if err := g.Adquirir(bg, 1, "r", c.a); err != nil {
				t.Fatal(err)
			}
			ctx, cancel := context.WithTimeout(bg, 30*time.Millisecond)
			defer cancel()
			err := g.Adquirir(ctx, 2, "r", c.b)
			if c.bloqueia && !errors.Is(err, context.DeadlineExceeded) {
				t.Fatalf("deveria bloquear até o timeout, err = %v", err)
			}
			if !c.bloqueia && err != nil {
				t.Fatalf("não deveria bloquear: %v", err)
			}
			if g.Esperando(2) {
				t.Fatal("tx 2 não deveria continuar na fila")
			}
		})
	}
}

func TestReentranteEPromocao(t *testing.T) {
	g := Novo()
	if err := g.Adquirir(bg, 1, "r", Exclusivo); err != nil {
		t.Fatal(err)
	}
	// já tem X: pedir S ou X de novo é imediato
	if g.Adquirir(bg, 1, "r", Compartilhado) != nil || g.Adquirir(bg, 1, "r", Exclusivo) != nil {
		t.Fatal("reentrada deveria ser imediata")
	}
	if m, _ := g.ModoDe(1, "r"); m != Exclusivo {
		t.Fatalf("modo = %v", m)
	}
	// S -> X quando é o único titular
	g.LiberarTudo(1)
	g.Adquirir(bg, 1, "r", Compartilhado)
	if err := g.Adquirir(bg, 1, "r", Exclusivo); err != nil {
		t.Fatalf("promoção: %v", err)
	}
	if m, _ := g.ModoDe(1, "r"); m != Exclusivo {
		t.Fatalf("modo após promoção = %v", m)
	}
}

func TestEsperaEConcessaoAoLiberar(t *testing.T) {
	g := Novo()
	g.Adquirir(bg, 1, "r", Exclusivo)
	feito := make(chan error, 1)
	go func() { feito <- g.Adquirir(bg, 2, "r", Compartilhado) }()
	aguardar(t, g, 2)
	select {
	case <-feito:
		t.Fatal("não deveria ter sido concedido ainda")
	case <-time.After(20 * time.Millisecond):
	}
	g.LiberarTudo(1)
	if err := <-feito; err != nil {
		t.Fatal(err)
	}
	if m, ok := g.ModoDe(2, "r"); !ok || m != Compartilhado {
		t.Fatalf("modo = %v %v", m, ok)
	}
	g.LiberarTudo(2)
	if g.Recursos() != 0 {
		t.Fatalf("recursos residuais: %d", g.Recursos())
	}
}

func TestVariosLeitoresLiberadosJuntos(t *testing.T) {
	g := Novo()
	g.Adquirir(bg, 1, "r", Exclusivo)
	var wg sync.WaitGroup
	for tx := TxID(2); tx <= 5; tx++ {
		wg.Add(1)
		go func(tx TxID) {
			defer wg.Done()
			if err := g.Adquirir(bg, tx, "r", Compartilhado); err != nil {
				t.Error(err)
			}
		}(tx)
	}
	for tx := TxID(2); tx <= 5; tx++ {
		aguardar(t, g, tx)
	}
	g.LiberarTudo(1)
	wg.Wait()
}

func TestDeadlockDeDois(t *testing.T) {
	g := Novo()
	g.Adquirir(bg, 1, "A", Exclusivo)
	g.Adquirir(bg, 2, "B", Exclusivo)
	feito := make(chan error, 1)
	go func() { feito <- g.Adquirir(bg, 1, "B", Exclusivo) }()
	aguardar(t, g, 1)
	// tx 2 pedir A fecha o ciclo 2 -> 1 -> 2
	if err := g.Adquirir(bg, 2, "A", Exclusivo); err != ErrDeadlock {
		t.Fatalf("err = %v", err)
	}
	if g.Esperando(2) {
		t.Fatal("vítima não deve ficar na fila")
	}
	g.LiberarTudo(2) // a vítima aborta
	if err := <-feito; err != nil {
		t.Fatalf("tx 1 deveria prosseguir: %v", err)
	}
}

func TestDeadlockDeTres(t *testing.T) {
	g := Novo()
	for i, r := range []string{"A", "B", "C"} {
		g.Adquirir(bg, TxID(i+1), r, Exclusivo)
	}
	feitos := make(chan error, 2)
	go func() { feitos <- g.Adquirir(bg, 1, "B", Exclusivo) }()
	aguardar(t, g, 1)
	go func() { feitos <- g.Adquirir(bg, 2, "C", Exclusivo) }()
	aguardar(t, g, 2)
	if err := g.Adquirir(bg, 3, "A", Exclusivo); err != ErrDeadlock {
		t.Fatalf("err = %v", err)
	}
	g.LiberarTudo(3)
	if err := <-feitos; err != nil { // tx 2 obtém C
		t.Fatal(err)
	}
	g.LiberarTudo(2)
	if err := <-feitos; err != nil { // tx 1 obtém B
		t.Fatal(err)
	}
}

func TestDeadlockDePromocao(t *testing.T) {
	g := Novo()
	g.Adquirir(bg, 1, "r", Compartilhado)
	g.Adquirir(bg, 2, "r", Compartilhado)
	feito := make(chan error, 1)
	go func() { feito <- g.Adquirir(bg, 1, "r", Exclusivo) }()
	aguardar(t, g, 1)
	if err := g.Adquirir(bg, 2, "r", Exclusivo); err != ErrDeadlock {
		t.Fatalf("err = %v", err)
	}
	g.LiberarTudo(2)
	if err := <-feito; err != nil {
		t.Fatal(err)
	}
	if m, _ := g.ModoDe(1, "r"); m != Exclusivo {
		t.Fatalf("modo = %v", m)
	}
}

func TestSemFalsoDeadlock(t *testing.T) {
	// 1 espera 2, 2 espera 3: cadeia sem ciclo
	g := Novo()
	g.Adquirir(bg, 2, "A", Exclusivo)
	g.Adquirir(bg, 3, "B", Exclusivo)
	feito := make(chan error, 2)
	go func() { feito <- g.Adquirir(bg, 1, "A", Exclusivo) }()
	aguardar(t, g, 1)
	go func() { feito <- g.Adquirir(bg, 2, "B", Exclusivo) }()
	aguardar(t, g, 2)
	g.LiberarTudo(3)
	if err := <-feito; err != nil {
		t.Fatal(err)
	}
	g.LiberarTudo(2)
	if err := <-feito; err != nil {
		t.Fatal(err)
	}
}

func TestCancelamentoPorContexto(t *testing.T) {
	g := Novo()
	g.Adquirir(bg, 1, "r", Exclusivo)
	ctx, cancel := context.WithCancel(bg)
	feito := make(chan error, 1)
	go func() { feito <- g.Adquirir(ctx, 2, "r", Exclusivo) }()
	aguardar(t, g, 2)
	cancel()
	if err := <-feito; !errors.Is(err, context.Canceled) {
		t.Fatalf("err = %v", err)
	}
	g.LiberarTudo(1)
	// o pedido cancelado não pode ter ficado na fila
	if err := g.Adquirir(bg, 3, "r", Exclusivo); err != nil {
		t.Fatal(err)
	}
}

func TestFase2PL(t *testing.T) {
	g := Novo()
	g.Adquirir(bg, 1, "a", Compartilhado)
	g.Adquirir(bg, 1, "b", Compartilhado)
	if !g.Liberar(1, "a") {
		t.Fatal("liberar deveria funcionar")
	}
	if g.Liberar(1, "a") || g.Liberar(1, "zzz") {
		t.Fatal("liberar sem possuir deveria devolver false")
	}
	if err := g.Adquirir(bg, 1, "c", Compartilhado); err != ErrFaseEncolhimento {
		t.Fatalf("err = %v", err)
	}
	g.LiberarTudo(1)
	if err := g.Adquirir(bg, 1, "c", Compartilhado); err != nil {
		t.Fatalf("após encerrar a transação: %v", err)
	}
}

func TestModoInvalido(t *testing.T) {
	if err := Novo().Adquirir(bg, 1, "r", Modo(9)); err != ErrModoInvalido {
		t.Fatalf("err = %v", err)
	}
}

func TestExclusaoMutuaSobEstresse(t *testing.T) {
	g := Novo()
	contas := make([]int, 5) // protegidas apenas pelos bloqueios
	nomes := []string{"c0", "c1", "c2", "c3", "c4"}
	var prox TxID
	var mu sync.Mutex
	novoTx := func() TxID { mu.Lock(); defer mu.Unlock(); prox++; return prox }

	var wg sync.WaitGroup
	var deadlocks, sucessos int
	for w := 0; w < 8; w++ {
		wg.Add(1)
		go func(w int) {
			defer wg.Done()
			r := rand.New(rand.NewSource(int64(w)))
			for i := 0; i < 150; i++ {
				de, para := r.Intn(5), r.Intn(5)
				if de == para {
					continue
				}
				tx := novoTx()
				ok := true
				for _, c := range []int{de, para} {
					if err := g.Adquirir(bg, tx, nomes[c], Exclusivo); err != nil {
						if err != ErrDeadlock {
							t.Error(err)
						}
						ok = false
						break
					}
				}
				if ok {
					contas[de]--
					contas[para]++
				}
				g.LiberarTudo(tx)
				mu.Lock()
				if ok {
					sucessos++
				} else {
					deadlocks++
				}
				mu.Unlock()
			}
		}(w)
	}
	wg.Wait()
	soma := 0
	for _, v := range contas {
		soma += v
	}
	if soma != 0 {
		t.Fatalf("soma das contas = %d", soma)
	}
	if sucessos == 0 {
		t.Fatal("nenhuma transação concluiu")
	}
	if g.Recursos() != 0 {
		t.Fatalf("recursos residuais: %d", g.Recursos())
	}
	t.Logf("sucessos=%d deadlocks resolvidos=%d", sucessos, deadlocks)
}
