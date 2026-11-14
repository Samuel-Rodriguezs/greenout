package bufferpool

import (
	"fmt"
	"path/filepath"
	"sync"
	"testing"
)

func TestCapacidadeInvalida(t *testing.T) {
	for _, c := range [][2]int{{0, 8}, {-1, 8}, {2, 0}} {
		if _, err := Novo(NovoDiscoMemoria(), c[0], c[1]); err != ErrCapacidade {
			t.Fatalf("%v: err = %v", c, err)
		}
	}
}

func TestAcertosEFaltas(t *testing.T) {
	p, _ := Novo(NovoDiscoMemoria(), 2, 8)
	for _, id := range []uint32{1, 2, 1, 1, 2} {
		if _, err := p.Buscar(id); err != nil {
			t.Fatal(err)
		}
		p.Liberar(id, false)
	}
	est := p.Estatisticas()
	if est.Faltas != 2 || est.Acertos != 3 || est.Despejos != 0 {
		t.Fatalf("est = %+v", est)
	}
}

func TestDespejoLRU(t *testing.T) {
	d := NovoDiscoMemoria()
	p, _ := Novo(d, 3, 8)
	buscarELiberar := func(id uint32) {
		if _, err := p.Buscar(id); err != nil {
			t.Fatal(err)
		}
		p.Liberar(id, false)
	}
	buscarELiberar(1)
	buscarELiberar(2)
	buscarELiberar(3)
	buscarELiberar(1) // 1 vira a mais recente; LRU = 2
	buscarELiberar(4) // despeja 2
	if p.Residentes() != 3 {
		t.Fatalf("residentes = %d", p.Residentes())
	}
	antes := p.Estatisticas().Faltas
	buscarELiberar(1) // ainda residente
	buscarELiberar(3)
	buscarELiberar(4)
	if p.Estatisticas().Faltas != antes {
		t.Fatal("1, 3 e 4 deveriam estar residentes")
	}
	buscarELiberar(2) // foi despejada: falta
	if p.Estatisticas().Faltas != antes+1 {
		t.Fatal("2 deveria ter sido despejada")
	}
}

func TestPaginaSujaGravadaNoDespejo(t *testing.T) {
	d := NovoDiscoMemoria()
	p, _ := Novo(d, 1, 4)
	q, _ := p.Buscar(7)
	copy(q.Dados, "abcd")
	p.Liberar(7, true)
	if d.Escritas != 0 {
		t.Fatal("não deveria gravar antes do despejo")
	}
	q2, _ := p.Buscar(8) // despeja a 7
	p.Liberar(8, false)
	_ = q2
	if d.Escritas != 1 {
		t.Fatalf("escritas = %d", d.Escritas)
	}
	q3, _ := p.Buscar(7)
	if string(q3.Dados) != "abcd" {
		t.Fatalf("dados relidos = %q", q3.Dados)
	}
	p.Liberar(7, false)
	// página limpa não gera escrita ao ser despejada
	p.Buscar(9)
	p.Liberar(9, false)
	if d.Escritas != 1 {
		t.Fatalf("escritas = %d, página limpa gravada", d.Escritas)
	}
}

func TestPoolCheioComTodasFixadas(t *testing.T) {
	p, _ := Novo(NovoDiscoMemoria(), 2, 4)
	p.Buscar(1)
	p.Buscar(2)
	if _, err := p.Buscar(3); err != ErrPoolCheio {
		t.Fatalf("err = %v", err)
	}
	p.Liberar(1, false)
	if _, err := p.Buscar(3); err != nil {
		t.Fatalf("depois de liberar: %v", err)
	}
}

func TestPinsMultiplos(t *testing.T) {
	p, _ := Novo(NovoDiscoMemoria(), 1, 4)
	p.Buscar(1)
	p.Buscar(1)
	p.Liberar(1, false)
	if _, err := p.Buscar(2); err != ErrPoolCheio {
		t.Fatalf("ainda há um pin: %v", err)
	}
	p.Liberar(1, false)
	if err := p.Liberar(1, false); err != ErrNaoFixada {
		t.Fatalf("liberar sem pin: %v", err)
	}
	if err := p.Liberar(99, false); err != ErrNaoFixada {
		t.Fatalf("liberar inexistente: %v", err)
	}
}

func TestDescarregar(t *testing.T) {
	d := NovoDiscoMemoria()
	p, _ := Novo(d, 4, 4)
	for id := uint32(0); id < 3; id++ {
		q, _ := p.Buscar(id)
		q.Dados[0] = byte('a' + id)
		p.Liberar(id, id != 1) // a 1 fica limpa
	}
	if err := p.Descarregar(); err != nil {
		t.Fatal(err)
	}
	if d.Escritas != 2 {
		t.Fatalf("escritas = %d", d.Escritas)
	}
	p.Descarregar()
	if d.Escritas != 2 {
		t.Fatal("segunda descarga não deveria gravar")
	}
}

type discoQuebrado struct{ DiscoMemoria }

func (d *discoQuebrado) EscreverPagina(uint32, []byte) error { return fmt.Errorf("disco cheio") }

func TestErroDeEscritaNoDespejo(t *testing.T) {
	p, _ := Novo(&discoQuebrado{DiscoMemoria{paginas: map[uint32][]byte{}}}, 1, 4)
	q, _ := p.Buscar(1)
	q.Dados[0] = 1
	p.Liberar(1, true)
	if _, err := p.Buscar(2); err == nil {
		t.Fatal("deveria propagar o erro de escrita")
	}
	if p.Residentes() != 1 {
		t.Fatal("página suja não pode ser perdida")
	}
}

func TestDiscoArquivo(t *testing.T) {
	caminho := filepath.Join(t.TempDir(), "paginas")
	d, err := AbrirDiscoArquivo(caminho, 16)
	if err != nil {
		t.Fatal(err)
	}
	p, _ := Novo(d, 2, 16)
	for id := uint32(0); id < 6; id++ {
		q, err := p.Buscar(id)
		if err != nil {
			t.Fatal(err)
		}
		copy(q.Dados, fmt.Sprintf("pagina-%d", id))
		p.Liberar(id, true)
	}
	p.Descarregar()
	d.Fechar()

	d2, _ := AbrirDiscoArquivo(caminho, 16)
	defer d2.Fechar()
	p2, _ := Novo(d2, 2, 16)
	for id := uint32(0); id < 6; id++ {
		q, _ := p2.Buscar(id)
		quer := fmt.Sprintf("pagina-%d", id)
		if string(q.Dados[:len(quer)]) != quer {
			t.Fatalf("página %d = %q", id, q.Dados)
		}
		p2.Liberar(id, false)
	}
	// além do fim do arquivo: zeros
	q, err := p2.Buscar(100)
	if err != nil {
		t.Fatal(err)
	}
	for _, b := range q.Dados {
		if b != 0 {
			t.Fatal("página inexistente deveria ser zeros")
		}
	}
}

func TestConcorrencia(t *testing.T) {
	p, _ := Novo(NovoDiscoMemoria(), 8, 8)
	var wg sync.WaitGroup
	for g := 0; g < 8; g++ {
		wg.Add(1)
		go func(g int) {
			defer wg.Done()
			for i := 0; i < 500; i++ {
				id := uint32((g*7 + i) % 20)
				q, err := p.Buscar(id)
				if err == ErrPoolCheio {
					continue
				}
				if err != nil {
					t.Error(err)
					return
				}
				p.Liberar(q.ID, i%5 == 0)
			}
		}(g)
	}
	wg.Wait()
	if p.Residentes() > 8 {
		t.Fatalf("residentes = %d", p.Residentes())
	}
}
