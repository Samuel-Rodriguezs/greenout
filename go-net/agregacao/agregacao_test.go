package agregacao

import (
	"reflect"
	"testing"

	"greenout/net/cidr"
	"greenout/net/ipv4"
)

func lista(ss ...string) []cidr.Prefixo {
	var out []cidr.Prefixo
	for _, s := range ss {
		out = append(out, cidr.MustParse(s))
	}
	return out
}

func strs(ps []cidr.Prefixo) []string {
	var out []string
	for _, p := range ps {
		out = append(out, p.String())
	}
	return out
}

func TestAgregar(t *testing.T) {
	casos := []struct {
		nome    string
		entrada []string
		want    []string
	}{
		{"vazio", nil, nil},
		{"um", []string{"10.0.0.0/8"}, []string{"10.0.0.0/8"}},
		{"irmaos", []string{"10.0.0.0/25", "10.0.0.128/25"}, []string{"10.0.0.0/24"}},
		{"irmaos fora de ordem", []string{"10.0.0.128/25", "10.0.0.0/25"}, []string{"10.0.0.0/24"}},
		{"cascata", []string{"10.0.0.0/26", "10.0.0.64/26", "10.0.0.128/26", "10.0.0.192/26"}, []string{"10.0.0.0/24"}},
		{"duplicados", []string{"10.0.0.0/24", "10.0.0.0/24"}, []string{"10.0.0.0/24"}},
		{"contido", []string{"10.0.0.0/8", "10.5.0.0/16", "10.9.9.0/24"}, []string{"10.0.0.0/8"}},
		{"nao adjacentes", []string{"10.0.0.0/24", "10.0.2.0/24"}, []string{"10.0.0.0/24", "10.0.2.0/24"}},
		{"adjacentes mas nao irmaos", []string{"10.0.1.0/24", "10.0.2.0/24"}, []string{"10.0.1.0/24", "10.0.2.0/24"}},
		{"lacuna impede fusao", []string{"10.0.0.0/24", "10.0.1.0/24", "10.0.3.0/24"}, []string{"10.0.0.0/23", "10.0.3.0/24"}},
		{"tamanhos diferentes", []string{"10.0.0.0/25", "10.0.0.128/26"}, []string{"10.0.0.0/25", "10.0.0.128/26"}},
		{"fusao completa para /0", []string{"0.0.0.0/1", "128.0.0.0/1"}, []string{"0.0.0.0/0"}},
		{"contido apos fusao", []string{"192.168.0.0/24", "192.168.1.0/24", "192.168.0.128/25"}, []string{"192.168.0.0/23"}},
		{"padrao 4 /24", []string{"172.16.0.0/24", "172.16.1.0/24", "172.16.2.0/24", "172.16.3.0/24"}, []string{"172.16.0.0/22"}},
	}
	for _, c := range casos {
		t.Run(c.nome, func(t *testing.T) {
			got := strs(Agregar(lista(c.entrada...)))
			if !reflect.DeepEqual(got, c.want) {
				t.Errorf("Agregar = %v, esperava %v", got, c.want)
			}
		})
	}
}

func TestAgregarNaoAlteraEntrada(t *testing.T) {
	in := lista("10.0.0.128/25", "10.0.0.0/25")
	Agregar(in)
	if in[0].String() != "10.0.0.128/25" || in[1].String() != "10.0.0.0/25" {
		t.Errorf("entrada alterada: %v", strs(in))
	}
}

// A agregação deve preservar exatamente o conjunto de endereços cobertos.
func TestAgregarPreservaCobertura(t *testing.T) {
	entrada := lista("10.0.0.0/26", "10.0.0.64/26", "10.0.0.192/26", "10.0.1.0/24", "10.0.2.0/25", "10.0.2.0/26")
	saida := Agregar(entrada)
	for ip := ipv4.MustParse("10.0.0.0"); ip < ipv4.MustParse("10.0.4.0"); ip++ {
		antes, depois := false, false
		for _, p := range entrada {
			antes = antes || p.Contem(ip)
		}
		for _, p := range saida {
			depois = depois || p.Contem(ip)
		}
		if antes != depois {
			t.Fatalf("cobertura difere em %s: antes=%v depois=%v (%v)", ip, antes, depois, strs(saida))
		}
	}
}

func TestCobre(t *testing.T) {
	c := lista("10.0.0.0/8", "192.168.0.0/16")
	if !Cobre(c, cidr.MustParse("10.1.2.0/24")) || Cobre(c, cidr.MustParse("11.0.0.0/8")) || Cobre(nil, cidr.MustParse("0.0.0.0/0")) {
		t.Error("Cobre incorreto")
	}
}
