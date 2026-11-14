package hll

import (
	"encoding/binary"
	"fmt"
	"hash/crc32"
	"math"
	"sync"
	"testing"
)

func preencher(h *HLL, prefixo string, de, ate int) {
	for i := de; i < ate; i++ {
		h.AdicionarString(fmt.Sprintf("%s-%d", prefixo, i))
	}
}

func TestPrecisaoInvalida(t *testing.T) {
	for _, p := range []uint8{0, 3, 17, 255} {
		if _, err := Novo(p); err != ErrPrecisao {
			t.Errorf("p=%d: err = %v", p, err)
		}
	}
}

func TestVazio(t *testing.T) {
	h, _ := Novo(12)
	if h.Estimativa() != 0 {
		t.Fatalf("estimativa de vazio = %d", h.Estimativa())
	}
}

func TestPrecisaoDaEstimativa(t *testing.T) {
	casos := []struct {
		p    uint8
		n    int
		erro float64 // erro relativo tolerado
	}{
		{14, 1, 0.01},
		{14, 10, 0.05},
		{14, 1000, 0.03},
		{14, 100000, 0.03},
		{12, 50000, 0.05},
		{10, 20000, 0.10},
		{16, 200000, 0.02},
	}
	for _, c := range casos {
		t.Run(fmt.Sprintf("p=%d n=%d", c.p, c.n), func(t *testing.T) {
			h, _ := Novo(c.p)
			preencher(h, "el", 0, c.n)
			est := float64(h.Estimativa())
			if rel := math.Abs(est-float64(c.n)) / float64(c.n); rel > c.erro {
				t.Fatalf("estimativa %.0f para %d (erro %.3f > %.3f)", est, c.n, rel, c.erro)
			}
		})
	}
}

func TestRepeticoesNaoMudamAEstimativa(t *testing.T) {
	h, _ := Novo(14)
	preencher(h, "a", 0, 5000)
	antes := h.Estimativa()
	for i := 0; i < 5; i++ {
		preencher(h, "a", 0, 5000)
	}
	if h.Estimativa() != antes {
		t.Fatalf("estimativa mudou: %d -> %d", antes, h.Estimativa())
	}
}

func TestElementoVazio(t *testing.T) {
	h, _ := Novo(10)
	h.Adicionar(nil)
	h.Adicionar([]byte{})
	if h.Estimativa() != 1 {
		t.Fatalf("estimativa = %d", h.Estimativa())
	}
}

func TestMesclar(t *testing.T) {
	a, _ := Novo(14)
	b, _ := Novo(14)
	preencher(a, "x", 0, 30000)
	preencher(b, "x", 20000, 50000) // 10 mil em comum
	if err := a.Mesclar(b); err != nil {
		t.Fatal(err)
	}
	est := float64(a.Estimativa())
	if rel := math.Abs(est-50000) / 50000; rel > 0.03 {
		t.Fatalf("união estimada em %.0f (erro %.3f)", est, rel)
	}
	if err := a.Mesclar(a); err != nil {
		t.Fatal(err)
	}
	c, _ := Novo(10)
	if err := a.Mesclar(c); err != ErrIncompativel {
		t.Fatalf("err = %v", err)
	}
	// o original de b não muda
	if e := float64(b.Estimativa()); math.Abs(e-30000)/30000 > 0.03 {
		t.Fatalf("b alterado: %.0f", e)
	}
}

func TestSerializacao(t *testing.T) {
	h, _ := Novo(11)
	preencher(h, "s", 0, 8000)
	b, _ := h.MarshalBinary()
	g, err := Carregar(b)
	if err != nil {
		t.Fatal(err)
	}
	if g.Estimativa() != h.Estimativa() {
		t.Fatalf("estimativas diferem: %d vs %d", g.Estimativa(), h.Estimativa())
	}
}

func TestCarregarInvalido(t *testing.T) {
	h, _ := Novo(6)
	preencher(h, "s", 0, 100)
	bom, _ := h.MarshalBinary()
	copia := func() []byte { return append([]byte(nil), bom...) }
	casos := []struct {
		nome string
		b    []byte
	}{
		{"nil", nil},
		{"curto", []byte{6, 1, 2}},
		{"precisão inválida", func() []byte { b := copia(); b[0] = 30; return b }()},
		{"registrador alterado", func() []byte { b := copia(); b[5] ^= 1; return b }()},
		{"crc alterado", func() []byte { b := copia(); b[len(b)-1] ^= 1; return b }()},
		{"truncado", copia()[:len(bom)-1]},
		{"sobrando", append(copia(), 0)},
	}
	for _, c := range casos {
		t.Run(c.nome, func(t *testing.T) {
			if _, err := Carregar(c.b); err != ErrFormato {
				t.Fatalf("err = %v", err)
			}
		})
	}
}

func TestRegistradorAcimaDoMaximoERejeitado(t *testing.T) {
	h, _ := Novo(4)
	b, _ := h.MarshalBinary()
	corpo := append([]byte(nil), b[:len(b)-4]...)
	corpo[1] = 200 // rank impossível para p=4
	// recalcula o crc para isolar a validação do rank
	b = binary.LittleEndian.AppendUint32(corpo, crc32.ChecksumIEEE(corpo))
	if _, err := Carregar(b); err != ErrFormato {
		t.Fatalf("err = %v", err)
	}
}

func TestConcorrencia(t *testing.T) {
	h, _ := Novo(12)
	var wg sync.WaitGroup
	for g := 0; g < 8; g++ {
		wg.Add(1)
		go func(g int) {
			defer wg.Done()
			preencher(h, "c", g*2500, (g+1)*2500)
			h.Estimativa()
		}(g)
	}
	wg.Wait()
	est := float64(h.Estimativa())
	if rel := math.Abs(est-20000) / 20000; rel > 0.05 {
		t.Fatalf("estimativa %.0f", est)
	}
}
