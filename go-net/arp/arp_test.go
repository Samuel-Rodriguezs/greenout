package arp

import (
	"sync"
	"testing"
	"time"

	"greenout/net/ipv4"
)

// relogioFalso é um relógio controlado pelo teste.
type relogioFalso struct {
	mu sync.Mutex
	t  time.Time
}

func (r *relogioFalso) Agora() time.Time {
	r.mu.Lock()
	defer r.mu.Unlock()
	return r.t
}

func (r *relogioFalso) Avanca(d time.Duration) {
	r.mu.Lock()
	r.t = r.t.Add(d)
	r.mu.Unlock()
}

func novoRelogio() *relogioFalso {
	return &relogioFalso{t: time.Date(2026, 1, 1, 12, 0, 0, 0, time.UTC)}
}

var (
	ip1  = ipv4.MustParse("192.168.0.1")
	ip2  = ipv4.MustParse("192.168.0.2")
	mac1 = MAC{0xde, 0xad, 0xbe, 0xef, 0x00, 0x01}
	mac2 = MAC{0xde, 0xad, 0xbe, 0xef, 0x00, 0x02}
)

func TestAprenderEBuscar(t *testing.T) {
	r := novoRelogio()
	tab := Nova(time.Minute, r.Agora)
	if _, ok := tab.Buscar(ip1); ok {
		t.Error("tabela vazia")
	}
	tab.Aprender(ip1, mac1)
	if m, ok := tab.Buscar(ip1); !ok || m != mac1 {
		t.Errorf("Buscar = %v %v", m, ok)
	}
	tab.Aprender(ip1, mac2) // atualização
	if m, _ := tab.Buscar(ip1); m != mac2 {
		t.Errorf("atualização: %v", m)
	}
}

func TestExpiracao(t *testing.T) {
	r := novoRelogio()
	tab := Nova(time.Minute, r.Agora)
	tab.Aprender(ip1, mac1)
	r.Avanca(59 * time.Second)
	if _, ok := tab.Buscar(ip1); !ok {
		t.Error("ainda deveria valer aos 59s")
	}
	r.Avanca(time.Second) // exatamente no TTL: vencida
	if _, ok := tab.Buscar(ip1); ok {
		t.Error("deveria expirar em 60s")
	}
	if tab.Tamanho() != 0 {
		t.Error("Buscar deveria remover a vencida")
	}
}

func TestRenovacaoReiniciaTTL(t *testing.T) {
	r := novoRelogio()
	tab := Nova(time.Minute, r.Agora)
	tab.Aprender(ip1, mac1)
	r.Avanca(50 * time.Second)
	tab.Aprender(ip1, mac1)
	r.Avanca(50 * time.Second)
	if _, ok := tab.Buscar(ip1); !ok {
		t.Error("renovação deveria estender a vida")
	}
}

func TestEstatica(t *testing.T) {
	r := novoRelogio()
	tab := Nova(time.Second, r.Agora)
	tab.DefinirEstatica(ip1, mac1)
	tab.Aprender(ip1, mac2) // não sobrescreve estática
	r.Avanca(24 * time.Hour)
	if m, ok := tab.Buscar(ip1); !ok || m != mac1 {
		t.Errorf("estática: %v %v", m, ok)
	}
	if tab.Varrer() != 0 {
		t.Error("Varrer não deve remover estáticas")
	}
}

func TestVarrerERemover(t *testing.T) {
	r := novoRelogio()
	tab := Nova(time.Minute, r.Agora)
	tab.Aprender(ip1, mac1)
	r.Avanca(40 * time.Second)
	tab.Aprender(ip2, mac2)
	r.Avanca(30 * time.Second) // ip1 com 70s (vencida), ip2 com 30s
	if n := tab.Varrer(); n != 1 {
		t.Errorf("Varrer = %d, esperava 1", n)
	}
	if _, ok := tab.Buscar(ip2); !ok || tab.Tamanho() != 1 {
		t.Error("ip2 deveria sobreviver")
	}
	if !tab.Remover(ip2) || tab.Remover(ip2) {
		t.Error("Remover deveria ser verdadeiro uma vez só")
	}
}

func TestRelogioPadrao(t *testing.T) {
	tab := Nova(time.Hour, nil)
	tab.Aprender(ip1, mac1)
	if _, ok := tab.Buscar(ip1); !ok {
		t.Error("com time.Now e TTL de 1h deveria existir")
	}
}

func TestConcorrencia(t *testing.T) {
	tab := Nova(time.Minute, nil)
	var wg sync.WaitGroup
	for i := 0; i < 8; i++ {
		wg.Add(1)
		go func(i int) {
			defer wg.Done()
			for j := 0; j < 200; j++ {
				ip := ipv4.Endereco(j % 16)
				tab.Aprender(ip, MAC{byte(i)})
				tab.Buscar(ip)
				tab.Varrer()
			}
		}(i)
	}
	wg.Wait()
}

func TestMACString(t *testing.T) {
	if got := mac1.String(); got != "de:ad:be:ef:00:01" {
		t.Errorf("MAC.String = %s", got)
	}
}
