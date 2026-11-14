// Pacote arp implementa uma tabela ARP (IPv4 -> MAC) com expiração por TTL e
// relógio injetável, para que o tempo possa ser controlado em testes.
package arp

import (
	"fmt"
	"sync"
	"time"

	"greenout/net/ipv4"
)

// MAC é um endereço Ethernet de 48 bits.
type MAC [6]byte

func (m MAC) String() string {
	return fmt.Sprintf("%02x:%02x:%02x:%02x:%02x:%02x", m[0], m[1], m[2], m[3], m[4], m[5])
}

// Relogio devolve o instante atual.
type Relogio func() time.Time

type entrada struct {
	mac      MAC
	expira   time.Time
	estatica bool
}

// Tabela é uma tabela ARP segura para uso concorrente.
type Tabela struct {
	mu       sync.Mutex
	ttl      time.Duration
	agora    Relogio
	entradas map[ipv4.Endereco]entrada
}

// Nova cria uma tabela cujas entradas dinâmicas vivem ttl. Se relogio for
// nil, usa time.Now.
func Nova(ttl time.Duration, relogio Relogio) *Tabela {
	if relogio == nil {
		relogio = time.Now
	}
	return &Tabela{ttl: ttl, agora: relogio, entradas: map[ipv4.Endereco]entrada{}}
}

// Aprender registra ou renova uma entrada dinâmica (ex.: ao receber um ARP
// reply). Não sobrescreve entradas estáticas.
func (t *Tabela) Aprender(ip ipv4.Endereco, mac MAC) {
	t.mu.Lock()
	defer t.mu.Unlock()
	if e, ok := t.entradas[ip]; ok && e.estatica {
		return
	}
	t.entradas[ip] = entrada{mac: mac, expira: t.agora().Add(t.ttl)}
}

// DefinirEstatica cria uma entrada permanente, que não expira.
func (t *Tabela) DefinirEstatica(ip ipv4.Endereco, mac MAC) {
	t.mu.Lock()
	defer t.mu.Unlock()
	t.entradas[ip] = entrada{mac: mac, estatica: true}
}

// Buscar devolve o MAC de ip se a entrada existir e não tiver expirado.
// Entradas vencidas são removidas.
func (t *Tabela) Buscar(ip ipv4.Endereco) (MAC, bool) {
	t.mu.Lock()
	defer t.mu.Unlock()
	e, ok := t.entradas[ip]
	if !ok {
		return MAC{}, false
	}
	if !e.estatica && !t.agora().Before(e.expira) {
		delete(t.entradas, ip)
		return MAC{}, false
	}
	return e.mac, true
}

// Remover apaga a entrada de ip e informa se ela existia.
func (t *Tabela) Remover(ip ipv4.Endereco) bool {
	t.mu.Lock()
	defer t.mu.Unlock()
	_, ok := t.entradas[ip]
	delete(t.entradas, ip)
	return ok
}

// Varrer remove todas as entradas vencidas e devolve quantas foram removidas.
func (t *Tabela) Varrer() int {
	t.mu.Lock()
	defer t.mu.Unlock()
	agora := t.agora()
	n := 0
	for ip, e := range t.entradas {
		if !e.estatica && !agora.Before(e.expira) {
			delete(t.entradas, ip)
			n++
		}
	}
	return n
}

// Tamanho devolve o número de entradas armazenadas (inclusive vencidas ainda
// não varridas).
func (t *Tabela) Tamanho() int {
	t.mu.Lock()
	defer t.mu.Unlock()
	return len(t.entradas)
}
