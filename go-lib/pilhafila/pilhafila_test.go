package pilhafila

import "testing"

func TestPilha(t *testing.T) {
	var p Pilha[int]
	if _, ok := p.Desempilhar(); ok {
		t.Fatal("vazia")
	}
	if _, ok := p.Topo(); ok {
		t.Fatal("topo vazia")
	}
	for i := 1; i <= 3; i++ {
		p.Empilhar(i)
	}
	if v, _ := p.Topo(); v != 3 || p.Tamanho() != 3 {
		t.Fatal("topo")
	}
	for _, want := range []int{3, 2, 1} {
		if v, ok := p.Desempilhar(); !ok || v != want {
			t.Fatalf("got %d want %d", v, want)
		}
	}
}

func TestFila(t *testing.T) {
	var f Fila[int]
	if _, ok := f.Desenfileirar(); ok {
		t.Fatal("vazia")
	}
	if _, ok := f.Frente(); ok {
		t.Fatal("frente vazia")
	}
	// volume suficiente para disparar compactação
	for i := 0; i < 200; i++ {
		f.Enfileirar(i)
	}
	if v, _ := f.Frente(); v != 0 {
		t.Fatal("frente")
	}
	for i := 0; i < 150; i++ {
		if v, ok := f.Desenfileirar(); !ok || v != i {
			t.Fatalf("got %d want %d", v, i)
		}
	}
	if f.Tamanho() != 50 {
		t.Fatalf("tamanho %d", f.Tamanho())
	}
	f.Enfileirar(999)
	for i := 150; i < 200; i++ {
		if v, _ := f.Desenfileirar(); v != i {
			t.Fatalf("got %d want %d", v, i)
		}
	}
	if v, _ := f.Desenfileirar(); v != 999 || f.Tamanho() != 0 {
		t.Fatal("último")
	}
}

func TestDeque(t *testing.T) {
	var d Deque[int]
	if _, ok := d.RemoverInicio(); ok {
		t.Fatal("vazio início")
	}
	if _, ok := d.RemoverFim(); ok {
		t.Fatal("vazio fim")
	}
	d.AdicionarFim(2)
	d.AdicionarFim(3)
	d.AdicionarInicio(1)
	d.AdicionarInicio(0)
	d.AdicionarFim(4) // força crescimento com buffer "girado"
	d.AdicionarFim(5)
	if d.Tamanho() != 6 {
		t.Fatalf("tamanho %d", d.Tamanho())
	}
	if v, _ := d.RemoverInicio(); v != 0 {
		t.Fatal("início")
	}
	if v, _ := d.RemoverFim(); v != 5 {
		t.Fatal("fim")
	}
	for _, want := range []int{1, 2, 3, 4} {
		if v, ok := d.RemoverInicio(); !ok || v != want {
			t.Fatalf("got %d want %d", v, want)
		}
	}
}

func TestDequeComoPilhaEFila(t *testing.T) {
	var d Deque[int]
	for i := 0; i < 100; i++ {
		d.AdicionarInicio(i)
	}
	for i := 0; i < 100; i++ {
		if v, _ := d.RemoverFim(); v != i {
			t.Fatalf("got %d want %d", v, i)
		}
	}
}
