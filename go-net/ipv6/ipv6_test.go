package ipv6

import "testing"

func TestParseEString(t *testing.T) {
	casos := []struct {
		entrada string
		canon   string
	}{
		{"::", "::"},
		{"::1", "::1"},
		{"2001:db8::", "2001:db8::"},
		{"2001:0db8:0000:0000:0000:ff00:0042:8329", "2001:db8::ff00:42:8329"},
		{"2001:DB8::FF00:42:8329", "2001:db8::ff00:42:8329"},
		{"1:2:3:4:5:6:7:8", "1:2:3:4:5:6:7:8"},
		{"1:0:0:2:0:0:0:3", "1:0:0:2::3"},      // maior sequência vence
		{"1:0:0:2:0:0:3:4", "1::2:0:0:3:4"},    // empate: a primeira
		{"1:2:3:4:5:6:7:0", "1:2:3:4:5:6:7:0"}, // zero isolado não comprime
		{"0:0:0:0:0:0:0:1", "::1"},
		{"fe80::1", "fe80::1"},
		{"::ffff:192.168.1.1", "::ffff:c0a8:101"},
		{"64:ff9b::10.0.0.1", "64:ff9b::a00:1"},
		{"1:2:3:4:5:6:1.2.3.4", "1:2:3:4:5:6:102:304"},
		{"1::8", "1::8"},
		{"::8", "::8"},
		{"1:2:3:4:5:6:7::", "1:2:3:4:5:6:7:0"},
	}
	for _, c := range casos {
		e, err := Parse(c.entrada)
		if err != nil {
			t.Errorf("Parse(%q): %v", c.entrada, err)
			continue
		}
		if got := e.String(); got != c.canon {
			t.Errorf("String(Parse(%q)) = %q, esperava %q", c.entrada, got, c.canon)
		}
		if e2, err := Parse(e.String()); err != nil || e2 != e {
			t.Errorf("ida e volta falhou para %q", c.entrada)
		}
	}
}

func TestParseInvalidos(t *testing.T) {
	for _, s := range []string{
		"", ":", ":::", "1::2::3", "1:2:3:4:5:6:7", "1:2:3:4:5:6:7:8:9",
		"12345::", "g::1", "1:2:3:4:5:6:7:8::", "::1:2:3:4:5:6:7:8",
		":1:2:3:4:5:6:7", "1:2:3:4:5:6:7:", "1.2.3.4::", "::1.2.3.4:5",
		"::256.1.1.1", "1:2:3:4:5:6:7:1.2.3.4", "1::2:", ":1::2", "-1::",
	} {
		if _, err := Parse(s); err == nil {
			t.Errorf("Parse(%q) deveria falhar", s)
		}
	}
}

func TestBytes(t *testing.T) {
	e := MustParse("2001:db8::1")
	if e[0] != 0x20 || e[1] != 0x01 || e[2] != 0x0d || e[3] != 0xb8 || e[15] != 1 {
		t.Errorf("bytes incorretos: %v", e)
	}
	if e.Grupo(0) != 0x2001 || e.Grupo(7) != 1 {
		t.Error("Grupo incorreto")
	}
}

func TestClassificacao(t *testing.T) {
	if !MustParse("::1").EhLoopback() || MustParse("::2").EhLoopback() {
		t.Error("EhLoopback")
	}
	if !MustParse("::").EhNaoEspecificado() || MustParse("::1").EhNaoEspecificado() {
		t.Error("EhNaoEspecificado")
	}
	if !MustParse("fe80::1").EhLinkLocal() || !MustParse("febf::1").EhLinkLocal() || MustParse("fec0::1").EhLinkLocal() {
		t.Error("EhLinkLocal")
	}
	if !MustParse("fd12::1").EhUnicoLocal() || !MustParse("fc00::1").EhUnicoLocal() || MustParse("fe00::1").EhUnicoLocal() {
		t.Error("EhUnicoLocal")
	}
}

func TestIPv4Mapeado(t *testing.T) {
	v4, ok := MustParse("::ffff:10.1.2.3").IPv4Mapeado()
	if !ok || v4.String() != "10.1.2.3" {
		t.Errorf("mapeado = %v %v", v4, ok)
	}
	if _, ok := MustParse("::fffe:10.1.2.3").IPv4Mapeado(); ok {
		t.Error("não deveria ser mapeado")
	}
	if _, ok := MustParse("1::ffff:10.1.2.3").IPv4Mapeado(); ok {
		t.Error("não deveria ser mapeado")
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
