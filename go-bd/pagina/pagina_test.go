package pagina

import (
	"bytes"
	"fmt"
	"math/rand"
	"testing"
)

func TestInserirELer(t *testing.T) {
	casos := []struct {
		nome string
		regs [][]byte
	}{
		{"um", [][]byte{[]byte("ola")}},
		{"vazio", [][]byte{{}}},
		{"varios", [][]byte{[]byte("a"), []byte("bbb"), []byte("cc"), {}}},
		{"binario", [][]byte{{0, 1, 2, 255}, {0}}},
	}
	for _, c := range casos {
		t.Run(c.nome, func(t *testing.T) {
			p := Nova()
			slots := make([]int, len(c.regs))
			for i, r := range c.regs {
				s, err := p.Inserir(r)
				if err != nil {
					t.Fatal(err)
				}
				slots[i] = s
			}
			for i, r := range c.regs {
				got, err := p.Ler(slots[i])
				if err != nil || !bytes.Equal(got, r) {
					t.Fatalf("slot %d: %v %v", slots[i], got, err)
				}
			}
		})
	}
}

func TestSlotInvalidoERemovido(t *testing.T) {
	p := Nova()
	s, _ := p.Inserir([]byte("x"))
	for _, i := range []int{-1, 1, 99} {
		if _, err := p.Ler(i); err != ErrSlotInvalido {
			t.Fatalf("ler(%d): %v", i, err)
		}
	}
	if err := p.Remover(s); err != nil {
		t.Fatal(err)
	}
	if _, err := p.Ler(s); err != ErrRemovido {
		t.Fatalf("ler removido: %v", err)
	}
	if err := p.Remover(s); err != ErrRemovido {
		t.Fatalf("remover duas vezes: %v", err)
	}
	if err := p.Atualizar(s, []byte("y")); err != ErrRemovido {
		t.Fatalf("atualizar removido: %v", err)
	}
}

func TestReaproveitaSlot(t *testing.T) {
	p := Nova()
	a, _ := p.Inserir([]byte("aaa"))
	b, _ := p.Inserir([]byte("bbb"))
	p.Remover(a)
	c, _ := p.Inserir([]byte("ccc"))
	if c != a || p.NumSlots() != 2 {
		t.Fatalf("slot reaproveitado = %d (quer %d), slots=%d", c, a, p.NumSlots())
	}
	if got, _ := p.Ler(b); string(got) != "bbb" {
		t.Fatal("registro vizinho alterado")
	}
}

func TestEncher(t *testing.T) {
	p := Nova()
	reg := bytes.Repeat([]byte("x"), 96)
	n := 0
	for {
		if _, err := p.Inserir(reg); err != nil {
			if err != ErrSemEspaco {
				t.Fatal(err)
			}
			break
		}
		n++
	}
	// 4096-8 = 4088; cada registro ocupa 100 bytes
	if n != 40 {
		t.Fatalf("cabem %d registros, quer 40", n)
	}
	if p.EspacoLivre() >= 100 {
		t.Fatalf("espaço livre %d deveria ser menor que um registro", p.EspacoLivre())
	}
}

func TestRegistroMaximoEExcesso(t *testing.T) {
	p := Nova()
	if _, err := p.Inserir(make([]byte, MaxRegistro)); err != nil {
		t.Fatalf("registro máximo: %v", err)
	}
	if p.EspacoLivre() != 0 {
		t.Fatalf("livre = %d", p.EspacoLivre())
	}
	if _, err := Nova().Inserir(make([]byte, MaxRegistro+1)); err != ErrSemEspaco {
		t.Fatalf("excesso: %v", err)
	}
}

func TestFragmentacaoCompactaAutomatico(t *testing.T) {
	p := Nova()
	reg := bytes.Repeat([]byte("a"), 1000)
	var slots []int
	for i := 0; i < 4; i++ {
		s, err := p.Inserir(reg)
		if err != nil {
			t.Fatal(err)
		}
		slots = append(slots, s)
	}
	// remove dois no meio: espaço total existe mas está fragmentado
	p.Remover(slots[1])
	p.Remover(slots[2])
	grande := bytes.Repeat([]byte("b"), 1900)
	s, err := p.Inserir(grande)
	if err != nil {
		t.Fatalf("deveria compactar e caber: %v", err)
	}
	if got, _ := p.Ler(s); !bytes.Equal(got, grande) {
		t.Fatal("conteúdo novo incorreto")
	}
	for _, i := range []int{slots[0], slots[3]} {
		if got, _ := p.Ler(i); !bytes.Equal(got, reg) {
			t.Fatalf("slot %d corrompido pela compactação", i)
		}
	}
}

func TestAtualizar(t *testing.T) {
	p := Nova()
	a, _ := p.Inserir([]byte("12345"))
	b, _ := p.Inserir([]byte("vizinho"))

	if err := p.Atualizar(a, []byte("12")); err != nil {
		t.Fatal(err)
	}
	if got, _ := p.Ler(a); string(got) != "12" {
		t.Fatalf("encolher: %q", got)
	}
	if err := p.Atualizar(a, []byte("muito maior que antes")); err != nil {
		t.Fatal(err)
	}
	if got, _ := p.Ler(a); string(got) != "muito maior que antes" {
		t.Fatalf("crescer: %q", got)
	}
	if got, _ := p.Ler(b); string(got) != "vizinho" {
		t.Fatalf("vizinho: %q", got)
	}
	// atualização impossível mantém o conteúdo
	if err := p.Atualizar(a, make([]byte, MaxRegistro)); err != ErrSemEspaco {
		t.Fatalf("err = %v", err)
	}
	if got, _ := p.Ler(a); string(got) != "muito maior que antes" {
		t.Fatal("falha de atualização alterou o registro")
	}
}

func TestSerializacaoIdaEVolta(t *testing.T) {
	p := Nova()
	r := rand.New(rand.NewSource(1))
	esperado := map[int][]byte{}
	for i := 0; i < 30; i++ {
		d := make([]byte, r.Intn(80))
		r.Read(d)
		s, err := p.Inserir(d)
		if err != nil {
			t.Fatal(err)
		}
		esperado[s] = d
	}
	p.Remover(3)
	delete(esperado, 3)

	b := p.Bytes()
	if len(b) != Tamanho {
		t.Fatalf("tamanho serializado = %d", len(b))
	}
	q, err := Carregar(b)
	if err != nil {
		t.Fatal(err)
	}
	for s, d := range esperado {
		got, err := q.Ler(s)
		if err != nil || !bytes.Equal(got, d) {
			t.Fatalf("slot %d divergiu", s)
		}
	}
	if _, err := q.Ler(3); err != ErrRemovido {
		t.Fatalf("slot 3: %v", err)
	}
}

func TestCarregarCorrompida(t *testing.T) {
	p := Nova()
	p.Inserir([]byte("dado importante"))
	bom := p.Bytes()

	casos := []struct {
		nome string
		muda func(b []byte) []byte
		quer error
	}{
		{"byte de dados invertido", func(b []byte) []byte { b[Tamanho-3] ^= 1; return b }, ErrChecksum},
		{"checksum alterado", func(b []byte) []byte { b[0] ^= 1; return b }, ErrChecksum},
		{"curta", func(b []byte) []byte { return b[:100] }, ErrCorrompida},
		{"longa", func(b []byte) []byte { return append(b, 0) }, ErrCorrompida},
		{"vazia", func(b []byte) []byte { return nil }, ErrCorrompida},
	}
	for _, c := range casos {
		t.Run(c.nome, func(t *testing.T) {
			b := c.muda(append([]byte(nil), bom...))
			if _, err := Carregar(b); err != c.quer {
				t.Fatalf("err = %v, quer %v", err, c.quer)
			}
		})
	}
}

func TestCarregarEstruturaInconsistenteComCRCValido(t *testing.T) {
	casos := []struct {
		nome string
		muda func(p *Pagina)
	}{
		{"slots demais", func(p *Pagina) { p.defNum(2000) }},
		{"fim além da página", func(p *Pagina) { p.defFim(Tamanho + 10) }},
		{"offset antes da área de dados", func(p *Pagina) { p.defSlot(0, cabecalho, 4) }},
		{"registro passa do fim", func(p *Pagina) { p.defSlot(0, Tamanho-2, 10) }},
	}
	for _, c := range casos {
		t.Run(c.nome, func(t *testing.T) {
			p := Nova()
			p.Inserir([]byte("abcd"))
			c.muda(p)
			if _, err := Carregar(p.Bytes()); err != ErrCorrompida {
				t.Fatalf("err = %v", err)
			}
		})
	}
}

func TestPaginaVaziaSerializa(t *testing.T) {
	q, err := Carregar(Nova().Bytes())
	if err != nil || q.NumSlots() != 0 || q.EspacoLivre() != Tamanho-cabecalho {
		t.Fatalf("err=%v", err)
	}
}

func TestAleatorioContraMapa(t *testing.T) {
	r := rand.New(rand.NewSource(3))
	p := Nova()
	ref := map[int][]byte{}
	for i := 0; i < 5000; i++ {
		switch r.Intn(3) {
		case 0:
			d := make([]byte, r.Intn(300))
			r.Read(d)
			if s, err := p.Inserir(d); err == nil {
				ref[s] = d
			}
		case 1:
			for s := range ref {
				if err := p.Remover(s); err != nil {
					t.Fatal(err)
				}
				delete(ref, s)
				break
			}
		default:
			for s := range ref {
				d := make([]byte, r.Intn(300))
				r.Read(d)
				if err := p.Atualizar(s, d); err == nil {
					ref[s] = d
				}
				break
			}
		}
		if i%250 == 0 {
			q, err := Carregar(p.Bytes())
			if err != nil {
				t.Fatalf("passo %d: %v", i, err)
			}
			p = q
		}
	}
	for s, d := range ref {
		if got, err := p.Ler(s); err != nil || !bytes.Equal(got, d) {
			t.Fatal(fmt.Sprintf("slot %d divergiu: %v", s, err))
		}
	}
}
