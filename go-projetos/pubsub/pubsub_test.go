package pubsub

import (
	"errors"
	"sync"
	"testing"
	"time"
)

func receber(t *testing.T, ch <-chan string) string {
	t.Helper()
	select {
	case m := <-ch:
		return m
	case <-time.After(time.Second):
		t.Fatal("timeout esperando mensagem")
		return ""
	}
}

func TestPublicarAssinar(t *testing.T) {
	b := Novo(4)
	a1, _ := b.Assinar("noticias")
	a2, _ := b.Assinar("noticias")
	outro, _ := b.Assinar("esportes")

	n, err := b.Publicar("noticias", "olá")
	if err != nil || n != 2 {
		t.Fatalf("Publicar = %d, %v", n, err)
	}
	if receber(t, a1) != "olá" || receber(t, a2) != "olá" {
		t.Error("mensagem incorreta")
	}
	select {
	case m := <-outro:
		t.Errorf("tópico errado recebeu %q", m)
	default:
	}
	if n, _ := b.Publicar("vazio", "x"); n != 0 {
		t.Errorf("sem assinantes: n = %d", n)
	}
}

func TestFilaCheiaDescarta(t *testing.T) {
	b := Novo(1)
	b.Assinar("t")
	b.Publicar("t", "1")
	if n, _ := b.Publicar("t", "2"); n != 0 {
		t.Errorf("fila cheia deveria descartar, entregues = %d", n)
	}
}

func TestCancelar(t *testing.T) {
	b := Novo(1)
	ch, _ := b.Assinar("t")
	b.Cancelar("t", ch)
	if _, ok := <-ch; ok {
		t.Error("channel deveria estar fechado")
	}
	if n, _ := b.Publicar("t", "x"); n != 0 {
		t.Errorf("n = %d", n)
	}
}

func TestFechar(t *testing.T) {
	b := Novo(1)
	ch, _ := b.Assinar("t")
	b.Fechar()
	b.Fechar() // idempotente
	if _, ok := <-ch; ok {
		t.Error("channel deveria estar fechado")
	}
	if _, err := b.Assinar("t"); !errors.Is(err, ErrFechado) {
		t.Errorf("erro = %v", err)
	}
	if _, err := b.Publicar("t", "x"); !errors.Is(err, ErrFechado) {
		t.Errorf("erro = %v", err)
	}
}

func TestConcorrencia(t *testing.T) {
	b := Novo(100)
	ch, _ := b.Assinar("t")
	var wg sync.WaitGroup
	for i := 0; i < 10; i++ {
		wg.Add(1)
		go func() {
			defer wg.Done()
			for j := 0; j < 10; j++ {
				b.Publicar("t", "m")
			}
		}()
	}
	wg.Wait()
	if len(ch) != 100 {
		t.Errorf("recebidas = %d, esperado 100", len(ch))
	}
}
