package cidr

import (
	"reflect"
	"testing"

	"greenout/net/ipv4"
)

func TestParse(t *testing.T) {
	casos := []struct {
		entrada string
		want    string
		erro    bool
	}{
		{"192.168.1.0/24", "192.168.1.0/24", false},
		{"192.168.1.77/24", "192.168.1.0/24", false}, // zera bits de host
		{"0.0.0.0/0", "0.0.0.0/0", false},
		{"10.1.2.3/32", "10.1.2.3/32", false},
		{"10.0.0.0", "", true},
		{"10.0.0.0/", "", true},
		{"10.0.0.0/33", "", true},
		{"10.0.0.0/-1", "", true},
		{"10.0.0.0/08", "", true},
		{"10.0.0.0/a", "", true},
		{"10.0.0/8", "", true},
		{"/8", "", true},
	}
	for _, c := range casos {
		p, err := Parse(c.entrada)
		if (err != nil) != c.erro {
			t.Errorf("Parse(%q) erro=%v", c.entrada, err)
			continue
		}
		if !c.erro && p.String() != c.want {
			t.Errorf("Parse(%q) = %s, esperava %s", c.entrada, p, c.want)
		}
	}
}

func TestPropriedades(t *testing.T) {
	casos := []struct {
		cidr                             string
		mascara, bcast, primeiro, ultimo string
		enderecos, hosts                 uint64
	}{
		{"192.168.1.0/24", "255.255.255.0", "192.168.1.255", "192.168.1.1", "192.168.1.254", 256, 254},
		{"10.0.0.0/8", "255.0.0.0", "10.255.255.255", "10.0.0.1", "10.255.255.254", 1 << 24, 1<<24 - 2},
		{"172.16.4.0/22", "255.255.252.0", "172.16.7.255", "172.16.4.1", "172.16.7.254", 1024, 1022},
		{"10.0.0.0/30", "255.255.255.252", "10.0.0.3", "10.0.0.1", "10.0.0.2", 4, 2},
		{"10.0.0.4/31", "255.255.255.254", "10.0.0.5", "10.0.0.4", "10.0.0.5", 2, 2},
		{"10.0.0.9/32", "255.255.255.255", "10.0.0.9", "10.0.0.9", "10.0.0.9", 1, 1},
		{"0.0.0.0/0", "0.0.0.0", "255.255.255.255", "0.0.0.1", "255.255.255.254", 1 << 32, 1<<32 - 2},
	}
	for _, c := range casos {
		p := MustParse(c.cidr)
		if p.Mascara().String() != c.mascara || p.Broadcast().String() != c.bcast ||
			p.PrimeiroHost().String() != c.primeiro || p.UltimoHost().String() != c.ultimo ||
			p.NumEnderecos() != c.enderecos || p.NumHosts() != c.hosts {
			t.Errorf("%s: mascara=%s bcast=%s prim=%s ult=%s end=%d hosts=%d", c.cidr,
				p.Mascara(), p.Broadcast(), p.PrimeiroHost(), p.UltimoHost(), p.NumEnderecos(), p.NumHosts())
		}
	}
	if got := MustParse("192.168.1.0/24").Curinga().String(); got != "0.0.0.255" {
		t.Errorf("Curinga = %s", got)
	}
}

func TestContencao(t *testing.T) {
	a := MustParse("10.0.0.0/8")
	b := MustParse("10.1.0.0/16")
	c := MustParse("11.0.0.0/8")
	if !a.Contem(ipv4.MustParse("10.255.0.1")) || a.Contem(ipv4.MustParse("11.0.0.0")) {
		t.Error("Contem")
	}
	if !a.ContemPrefixo(b) || b.ContemPrefixo(a) || !a.ContemPrefixo(a) {
		t.Error("ContemPrefixo")
	}
	if !a.Sobrepoe(b) || !b.Sobrepoe(a) || a.Sobrepoe(c) {
		t.Error("Sobrepoe")
	}
	if MustParse("0.0.0.0/0").Contem(ipv4.MustParse("200.1.1.1")) != true {
		t.Error("/0 deve conter tudo")
	}
}

func TestPai(t *testing.T) {
	if got := MustParse("10.0.1.0/24").Pai().String(); got != "10.0.0.0/23" {
		t.Errorf("Pai = %s", got)
	}
	if got := MustParse("0.0.0.0/0").Pai().String(); got != "0.0.0.0/0" {
		t.Errorf("Pai(/0) = %s", got)
	}
}

func TestDivide(t *testing.T) {
	subs, err := MustParse("192.168.0.0/24").Divide(26)
	if err != nil {
		t.Fatal(err)
	}
	var got []string
	for _, s := range subs {
		got = append(got, s.String())
	}
	want := []string{"192.168.0.0/26", "192.168.0.64/26", "192.168.0.128/26", "192.168.0.192/26"}
	if !reflect.DeepEqual(got, want) {
		t.Errorf("Divide = %v", got)
	}
	if subs, err := MustParse("10.0.0.0/24").Divide(24); err != nil || len(subs) != 1 {
		t.Errorf("Divide mesmo tamanho: %v %v", subs, err)
	}
	for _, n := range []int{23, 33, -1} {
		if _, err := MustParse("10.0.0.0/24").Divide(n); err == nil {
			t.Errorf("Divide(%d) deveria falhar", n)
		}
	}
	if _, err := MustParse("0.0.0.0/0").Divide(32); err == nil {
		t.Error("divisão gigante deveria falhar")
	}
}

func TestTamanhoParaHosts(t *testing.T) {
	casos := map[int]int{1: 30, 2: 30, 3: 29, 6: 29, 7: 28, 50: 26, 100: 25, 254: 24, 255: 23, 1000: 22}
	for hosts, want := range casos {
		got, err := TamanhoParaHosts(hosts)
		if err != nil || got != want {
			t.Errorf("TamanhoParaHosts(%d) = %d, %v; esperava %d", hosts, got, err, want)
		}
	}
	for _, n := range []int{0, -5, 1 << 33} {
		if _, err := TamanhoParaHosts(n); err == nil {
			t.Errorf("TamanhoParaHosts(%d) deveria falhar", n)
		}
	}
}

func TestVLSM(t *testing.T) {
	rede := MustParse("192.168.10.0/24")
	// Pedidos fora de ordem: 50, 100, 10, 2 hosts.
	got, err := VLSM(rede, []int{50, 100, 10, 2})
	if err != nil {
		t.Fatal(err)
	}
	want := []string{"192.168.10.128/26", "192.168.10.0/25", "192.168.10.192/28", "192.168.10.208/30"}
	for i, p := range got {
		if p.String() != want[i] {
			t.Errorf("VLSM[%d] = %s, esperava %s", i, p, want[i])
		}
		if !rede.ContemPrefixo(p) {
			t.Errorf("%s fora de %s", p, rede)
		}
		for j := i + 1; j < len(got); j++ {
			if p.Sobrepoe(got[j]) {
				t.Errorf("%s sobrepõe %s", p, got[j])
			}
		}
	}
}

func TestVLSMErros(t *testing.T) {
	rede := MustParse("10.0.0.0/24")
	if _, err := VLSM(rede, []int{100, 100, 100}); err == nil {
		t.Error("deveria faltar espaço")
	}
	if _, err := VLSM(rede, []int{1000}); err == nil {
		t.Error("requisito maior que a rede deveria falhar")
	}
	if _, err := VLSM(rede, []int{0}); err == nil {
		t.Error("0 hosts deveria falhar")
	}
	if got, err := VLSM(rede, nil); err != nil || len(got) != 0 {
		t.Errorf("sem requisitos: %v %v", got, err)
	}
	// Cabe exatamente.
	if _, err := VLSM(rede, []int{126, 126}); err != nil {
		t.Errorf("deveria caber: %v", err)
	}
}

func TestMustParsePanica(t *testing.T) {
	defer func() {
		if recover() == nil {
			t.Error("esperava pânico")
		}
	}()
	MustParse("x")
}
