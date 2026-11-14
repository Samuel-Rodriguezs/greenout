package lab

import "testing"

func TestPilhaGen(t *testing.T) {
	var p PilhaGen[int]
	if _, err := p.Desempilhar(); err != ErrEstruturaVazia {
		t.Fatalf("esperava ErrEstruturaVazia, got %v", err)
	}
	if _, err := p.Topo(); err != ErrEstruturaVazia {
		t.Fatalf("esperava ErrEstruturaVazia, got %v", err)
	}
	for i := 1; i <= 3; i++ {
		p.Empilhar(i)
	}
	if p.Tamanho() != 3 {
		t.Fatalf("tamanho = %d", p.Tamanho())
	}
	if v, _ := p.Topo(); v != 3 {
		t.Fatalf("topo = %d", v)
	}
	for _, want := range []int{3, 2, 1} {
		v, err := p.Desempilhar()
		if err != nil || v != want {
			t.Fatalf("got %d, %v; want %d", v, err, want)
		}
	}
	if p.Tamanho() != 0 {
		t.Fatalf("deveria estar vazia")
	}
}

func TestFilaGen(t *testing.T) {
	var f FilaGen[string]
	if _, err := f.Desenfileirar(); err != ErrEstruturaVazia {
		t.Fatalf("esperava ErrEstruturaVazia, got %v", err)
	}
	if _, err := f.Frente(); err != ErrEstruturaVazia {
		t.Fatalf("esperava ErrEstruturaVazia, got %v", err)
	}
	for _, s := range []string{"a", "b", "c"} {
		f.Enfileirar(s)
	}
	if v, _ := f.Frente(); v != "a" || f.Tamanho() != 3 {
		t.Fatalf("frente = %q, tamanho = %d", v, f.Tamanho())
	}
	for _, want := range []string{"a", "b", "c"} {
		v, err := f.Desenfileirar()
		if err != nil || v != want {
			t.Fatalf("got %q, %v; want %q", v, err, want)
		}
	}
	f.Enfileirar("d")
	if v, _ := f.Desenfileirar(); v != "d" {
		t.Fatalf("reuso falhou: %q", v)
	}
}
