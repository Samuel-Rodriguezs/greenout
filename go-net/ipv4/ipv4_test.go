package ipv4

import "testing"

func TestParse(t *testing.T) {
	casos := []struct {
		entrada string
		want    Endereco
		erro    bool
	}{
		{"0.0.0.0", 0, false},
		{"255.255.255.255", 0xFFFFFFFF, false},
		{"192.168.0.1", 0xC0A80001, false},
		{"10.0.0.255", 0x0A0000FF, false},
		{"", 0, true},
		{"1.2.3", 0, true},
		{"1.2.3.4.5", 0, true},
		{"256.1.1.1", 0, true},
		{"1.2.3.-4", 0, true},
		{"01.2.3.4", 0, true},
		{"1..3.4", 0, true},
		{" 1.2.3.4", 0, true},
		{"1.2.3.4 ", 0, true},
		{"a.b.c.d", 0, true},
		{"1.2.3.1000", 0, true},
		{"+1.2.3.4", 0, true},
	}
	for _, c := range casos {
		got, err := Parse(c.entrada)
		if (err != nil) != c.erro {
			t.Errorf("Parse(%q) erro=%v, esperava erro=%v", c.entrada, err, c.erro)
			continue
		}
		if !c.erro && got != c.want {
			t.Errorf("Parse(%q) = %#x, esperava %#x", c.entrada, uint32(got), uint32(c.want))
		}
	}
}

func TestStringIdaEVolta(t *testing.T) {
	for _, s := range []string{"0.0.0.0", "1.2.3.4", "127.0.0.1", "255.255.255.255", "172.16.254.3"} {
		if got := MustParse(s).String(); got != s {
			t.Errorf("String(Parse(%q)) = %q", s, got)
		}
	}
}

func TestOctetos(t *testing.T) {
	e := MustParse("10.20.30.40")
	if o := e.Octetos(); o != [4]byte{10, 20, 30, 40} {
		t.Errorf("Octetos = %v", o)
	}
	if DeOctetos([4]byte{10, 20, 30, 40}) != e {
		t.Error("DeOctetos não inverte Octetos")
	}
}

func TestClassificacao(t *testing.T) {
	casos := []struct {
		ip                           string
		privado, loop, multi, linklc bool
	}{
		{"10.1.2.3", true, false, false, false},
		{"172.16.0.1", true, false, false, false},
		{"172.31.255.255", true, false, false, false},
		{"172.32.0.1", false, false, false, false},
		{"172.15.255.255", false, false, false, false},
		{"192.168.5.5", true, false, false, false},
		{"192.169.0.1", false, false, false, false},
		{"127.0.0.1", false, true, false, false},
		{"224.0.0.251", false, false, true, false},
		{"239.255.255.250", false, false, true, false},
		{"240.0.0.1", false, false, false, false},
		{"169.254.10.10", false, false, false, true},
		{"8.8.8.8", false, false, false, false},
	}
	for _, c := range casos {
		e := MustParse(c.ip)
		if e.EhPrivado() != c.privado || e.EhLoopback() != c.loop || e.EhMulticast() != c.multi || e.EhLinkLocal() != c.linklc {
			t.Errorf("classificação errada para %s", c.ip)
		}
	}
}

func TestMustParsePanica(t *testing.T) {
	defer func() {
		if recover() == nil {
			t.Error("esperava pânico")
		}
	}()
	MustParse("lixo")
}
