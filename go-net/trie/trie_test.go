package trie

import (
	"testing"

	"greenout/net/cidr"
	"greenout/net/ipv4"
)

func tabela() *Trie[string] {
	t := Nova[string]()
	t.Inserir(cidr.MustParse("0.0.0.0/0"), "default")
	t.Inserir(cidr.MustParse("10.0.0.0/8"), "A")
	t.Inserir(cidr.MustParse("10.1.0.0/16"), "B")
	t.Inserir(cidr.MustParse("10.1.2.0/24"), "C")
	t.Inserir(cidr.MustParse("192.168.1.1/32"), "host")
	return t
}

func TestBuscaLPM(t *testing.T) {
	tr := tabela()
	casos := []struct {
		ip     string
		prefix string
		valor  string
	}{
		{"10.1.2.3", "10.1.2.0/24", "C"},
		{"10.1.3.3", "10.1.0.0/16", "B"},
		{"10.2.0.1", "10.0.0.0/8", "A"},
		{"11.0.0.1", "0.0.0.0/0", "default"},
		{"192.168.1.1", "192.168.1.1/32", "host"},
		{"192.168.1.2", "0.0.0.0/0", "default"},
		{"10.1.2.255", "10.1.2.0/24", "C"},
	}
	for _, c := range casos {
		p, v, ok := tr.Buscar(ipv4.MustParse(c.ip))
		if !ok || p.String() != c.prefix || v != c.valor {
			t.Errorf("Buscar(%s) = %s %q %v; esperava %s %q", c.ip, p, v, ok, c.prefix, c.valor)
		}
	}
}

func TestBuscaSemRotaPadrao(t *testing.T) {
	tr := Nova[int]()
	if _, _, ok := tr.Buscar(ipv4.MustParse("1.1.1.1")); ok {
		t.Error("trie vazia não deve casar")
	}
	tr.Inserir(cidr.MustParse("10.0.0.0/8"), 1)
	if _, _, ok := tr.Buscar(ipv4.MustParse("11.1.1.1")); ok {
		t.Error("sem rota padrão não deve casar")
	}
	if _, v, ok := tr.Buscar(ipv4.MustParse("10.0.0.0")); !ok || v != 1 {
		t.Error("deveria casar 10.0.0.0")
	}
}

func TestInserirSubstitui(t *testing.T) {
	tr := Nova[int]()
	p := cidr.MustParse("10.0.0.0/8")
	tr.Inserir(p, 1)
	tr.Inserir(p, 2)
	if tr.Tamanho() != 1 {
		t.Errorf("Tamanho = %d", tr.Tamanho())
	}
	if v, ok := tr.Obter(p); !ok || v != 2 {
		t.Errorf("Obter = %d %v", v, ok)
	}
	if _, ok := tr.Obter(cidr.MustParse("10.0.0.0/9")); ok {
		t.Error("Obter deve ser exato")
	}
	if _, ok := tr.Obter(cidr.MustParse("10.0.0.0/7")); ok {
		t.Error("Obter de nó intermediário não deve existir")
	}
}

func TestRemover(t *testing.T) {
	tr := tabela()
	if !tr.Remover(cidr.MustParse("10.1.2.0/24")) {
		t.Fatal("Remover deveria ter sucesso")
	}
	if tr.Remover(cidr.MustParse("10.1.2.0/24")) {
		t.Error("segunda remoção deveria falhar")
	}
	if tr.Remover(cidr.MustParse("172.16.0.0/12")) {
		t.Error("remover inexistente deveria falhar")
	}
	if tr.Remover(cidr.MustParse("10.1.2.0/23")) {
		t.Error("remover nó intermediário sem valor deveria falhar")
	}
	if p, v, _ := tr.Buscar(ipv4.MustParse("10.1.2.3")); p.String() != "10.1.0.0/16" || v != "B" {
		t.Errorf("após remover, esperava cair em /16, obteve %s %s", p, v)
	}
	if tr.Tamanho() != 4 {
		t.Errorf("Tamanho = %d", tr.Tamanho())
	}
	// Remover tudo deixa a trie sem filhos (poda).
	for _, s := range []string{"0.0.0.0/0", "10.0.0.0/8", "10.1.0.0/16", "192.168.1.1/32"} {
		tr.Remover(cidr.MustParse(s))
	}
	if tr.Tamanho() != 0 || tr.raiz.filho[0] != nil || tr.raiz.filho[1] != nil {
		t.Error("trie deveria estar vazia e podada")
	}
}

func TestPercorrerOrdem(t *testing.T) {
	var got []string
	tabela().Percorrer(func(p cidr.Prefixo, v string) bool {
		got = append(got, p.String())
		return true
	})
	want := []string{"0.0.0.0/0", "10.0.0.0/8", "10.1.0.0/16", "10.1.2.0/24", "192.168.1.1/32"}
	if len(got) != len(want) {
		t.Fatalf("Percorrer = %v", got)
	}
	for i := range want {
		if got[i] != want[i] {
			t.Errorf("Percorrer[%d] = %s, esperava %s", i, got[i], want[i])
		}
	}
	n := 0
	tabela().Percorrer(func(cidr.Prefixo, string) bool { n++; return n < 2 })
	if n != 2 {
		t.Errorf("interrupção: visitou %d", n)
	}
}

// Confronta a trie com uma busca linear ingênua.
func TestContraBuscaLinear(t *testing.T) {
	prefixos := []string{"0.0.0.0/1", "128.0.0.0/2", "10.0.0.0/8", "10.128.0.0/9", "172.16.0.0/12", "172.20.0.0/14", "200.1.1.0/24"}
	tr := Nova[int]()
	var ps []cidr.Prefixo
	for i, s := range prefixos {
		p := cidr.MustParse(s)
		ps = append(ps, p)
		tr.Inserir(p, i)
	}
	for ip := uint64(0); ip < 1<<32; ip += 0x01234567 {
		e := ipv4.Endereco(ip)
		melhor, idx := -1, -1
		for i, p := range ps {
			if p.Contem(e) && p.Tam > melhor {
				melhor, idx = p.Tam, i
			}
		}
		_, v, ok := tr.Buscar(e)
		if (idx >= 0) != ok || (ok && v != idx) {
			t.Fatalf("divergência em %s: trie=%d,%v linear=%d", e, v, ok, idx)
		}
	}
}
