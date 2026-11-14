package nat

import (
	"errors"
	"testing"
	"time"

	"greenout/net/ipv4"
)

type relogio struct{ t time.Time }

func (r *relogio) Agora() time.Time       { return r.t }
func (r *relogio) Avanca(d time.Duration) { r.t = r.t.Add(d) }
func novoRelogio() *relogio               { return &relogio{time.Date(2026, 1, 1, 0, 0, 0, 0, time.UTC)} }

var publico = ipv4.MustParse("203.0.113.5")

func host(ip string, porta uint16) Ponto { return Ponto{ipv4.MustParse(ip), porta} }

func TestTraduzirEReverter(t *testing.T) {
	r := novoRelogio()
	tab, err := Nova(publico, 40000, 40009, time.Minute, r.Agora)
	if err != nil {
		t.Fatal(err)
	}
	a, b := host("10.0.0.1", 5000), host("10.0.0.2", 5000)
	pa, err := tab.Traduzir(a, TCP)
	if err != nil || pa.IP != publico || pa.Porta != 40000 {
		t.Fatalf("a: %+v %v", pa, err)
	}
	pb, _ := tab.Traduzir(b, TCP)
	if pb.Porta != 40001 {
		t.Errorf("b deveria receber porta distinta: %d", pb.Porta)
	}
	if p, _ := tab.Traduzir(a, TCP); p != pa {
		t.Errorf("mapeamento deveria ser estável: %+v != %+v", p, pa)
	}
	if got, ok := tab.Reverter(pa.Porta, TCP); !ok || got != a {
		t.Errorf("Reverter(a) = %+v %v", got, ok)
	}
	if got, ok := tab.Reverter(pb.Porta, TCP); !ok || got != b {
		t.Errorf("Reverter(b) = %+v %v", got, ok)
	}
	if tab.Tamanho() != 2 {
		t.Errorf("Tamanho = %d", tab.Tamanho())
	}
}

func TestProtocolosIndependentes(t *testing.T) {
	tab, _ := Nova(publico, 1000, 1010, time.Minute, nil)
	a := host("10.0.0.1", 53)
	pt, _ := tab.Traduzir(a, TCP)
	pu, _ := tab.Traduzir(a, UDP)
	if pt.Porta == pu.Porta {
		t.Error("TCP e UDP deveriam ter mapeamentos separados")
	}
	if _, ok := tab.Reverter(pt.Porta, UDP); ok {
		t.Error("porta de TCP não deve reverter como UDP")
	}
}

func TestPortaDesconhecida(t *testing.T) {
	tab, _ := Nova(publico, 1000, 1010, time.Minute, nil)
	if _, ok := tab.Reverter(1005, TCP); ok {
		t.Error("sem mapeamento não deve reverter")
	}
}

func TestExpiracaoLiberaPorta(t *testing.T) {
	r := novoRelogio()
	tab, _ := Nova(publico, 2000, 2000, 30*time.Second, r.Agora) // uma única porta
	a, b := host("10.0.0.1", 1), host("10.0.0.2", 2)
	if _, err := tab.Traduzir(a, UDP); err != nil {
		t.Fatal(err)
	}
	if _, err := tab.Traduzir(b, UDP); !errors.Is(err, ErrSemPortas) {
		t.Fatalf("esperava esgotamento, veio %v", err)
	}
	r.Avanca(30 * time.Second)
	if _, ok := tab.Reverter(2000, UDP); ok {
		t.Error("mapeamento expirado não deve reverter")
	}
	p, err := tab.Traduzir(b, UDP)
	if err != nil || p.Porta != 2000 {
		t.Errorf("porta deveria ser reaproveitada: %+v %v", p, err)
	}
	if tab.Tamanho() != 1 {
		t.Errorf("Tamanho = %d", tab.Tamanho())
	}
}

func TestTrafegoDeSaidaRenovaPrazo(t *testing.T) {
	r := novoRelogio()
	tab, _ := Nova(publico, 3000, 3005, time.Minute, r.Agora)
	a := host("10.0.0.1", 1)
	p, _ := tab.Traduzir(a, TCP)
	r.Avanca(45 * time.Second)
	tab.Traduzir(a, TCP) // renova
	r.Avanca(45 * time.Second)
	if _, ok := tab.Reverter(p.Porta, TCP); !ok {
		t.Error("saída recente deveria manter o mapeamento")
	}
	// Tráfego de entrada não renova.
	r.Avanca(15 * time.Second)
	if _, ok := tab.Reverter(p.Porta, TCP); ok {
		t.Error("entrada não deveria ter renovado o prazo")
	}
}

func TestEsgotamentoEReciclagemCircular(t *testing.T) {
	tab, _ := Nova(publico, 100, 102, time.Hour, nil)
	for i := 0; i < 3; i++ {
		if _, err := tab.Traduzir(host("10.0.0.1", uint16(i+1)), TCP); err != nil {
			t.Fatal(err)
		}
	}
	if _, err := tab.Traduzir(host("10.0.0.1", 99), TCP); !errors.Is(err, ErrSemPortas) {
		t.Errorf("deveria esgotar: %v", err)
	}
	// Mesmo protocolo esgotado, outro protocolo ainda tem portas.
	if _, err := tab.Traduzir(host("10.0.0.1", 99), UDP); err != nil {
		t.Errorf("UDP tem portas próprias: %v", err)
	}
}

func TestIntervaloInvalido(t *testing.T) {
	if _, err := Nova(publico, 0, 10, time.Second, nil); err == nil {
		t.Error("porta 0 deveria ser rejeitada")
	}
	if _, err := Nova(publico, 20, 10, time.Second, nil); err == nil {
		t.Error("min > max deveria ser rejeitado")
	}
}
