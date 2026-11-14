// Pacote cidr trata prefixos IPv4 em notação CIDR: parse, máscaras,
// divisão em sub-redes de mesmo tamanho e alocação VLSM.
package cidr

import (
	"errors"
	"fmt"
	"sort"
	"strconv"
	"strings"

	"greenout/net/ipv4"
)

// Prefixo é uma rede IPv4: endereço base (bits de host zerados) e tamanho.
type Prefixo struct {
	Base ipv4.Endereco
	Tam  int // comprimento do prefixo, 0 a 32
}

// Erros conhecidos.
var (
	ErrFormato   = errors.New("cidr: formato inválido")
	ErrTamanho   = errors.New("cidr: tamanho de prefixo inválido")
	ErrSemEspaco = errors.New("cidr: espaço insuficiente na rede")
)

// Parse lê "a.b.c.d/n". Bits de host são zerados (192.168.1.5/24 vira
// 192.168.1.0/24).
func Parse(s string) (Prefixo, error) {
	end, tam, ok := strings.Cut(s, "/")
	if !ok {
		return Prefixo{}, fmt.Errorf("%w: %q", ErrFormato, s)
	}
	ip, err := ipv4.Parse(end)
	if err != nil {
		return Prefixo{}, fmt.Errorf("%w: %v", ErrFormato, err)
	}
	if tam == "" || (len(tam) > 1 && tam[0] == '0') {
		return Prefixo{}, fmt.Errorf("%w: %q", ErrFormato, s)
	}
	for i := 0; i < len(tam); i++ {
		if tam[i] < '0' || tam[i] > '9' {
			return Prefixo{}, fmt.Errorf("%w: %q", ErrFormato, s)
		}
	}
	n, err := strconv.Atoi(tam)
	if err != nil || n > 32 {
		return Prefixo{}, fmt.Errorf("%w: /%s", ErrTamanho, tam)
	}
	return Novo(ip, n), nil
}

// MustParse é como Parse, mas entra em pânico em caso de erro.
func MustParse(s string) Prefixo {
	p, err := Parse(s)
	if err != nil {
		panic(err)
	}
	return p
}

// Novo cria um prefixo zerando os bits de host. Tam deve estar entre 0 e 32.
func Novo(ip ipv4.Endereco, tam int) Prefixo {
	return Prefixo{Base: ip & mascara(tam), Tam: tam}
}

func mascara(tam int) ipv4.Endereco {
	if tam <= 0 {
		return 0
	}
	return ipv4.Endereco(^uint32(0) << uint(32-tam))
}

// String formata como "a.b.c.d/n".
func (p Prefixo) String() string { return p.Base.String() + "/" + strconv.Itoa(p.Tam) }

// Mascara devolve a máscara de rede (ex.: /24 -> 255.255.255.0).
func (p Prefixo) Mascara() ipv4.Endereco { return mascara(p.Tam) }

// Curinga devolve a máscara invertida (wildcard).
func (p Prefixo) Curinga() ipv4.Endereco { return ^mascara(p.Tam) }

// Broadcast devolve o último endereço do bloco.
func (p Prefixo) Broadcast() ipv4.Endereco { return p.Base | p.Curinga() }

// NumEnderecos devolve o total de endereços do bloco (2^(32-Tam)).
func (p Prefixo) NumEnderecos() uint64 { return uint64(1) << uint(32-p.Tam) }

// NumHosts devolve a quantidade de hosts utilizáveis. /31 (RFC 3021) tem 2 e
// /32 tem 1; nos demais, descontam-se rede e broadcast.
func (p Prefixo) NumHosts() uint64 {
	switch p.Tam {
	case 32:
		return 1
	case 31:
		return 2
	}
	return p.NumEnderecos() - 2
}

// PrimeiroHost devolve o primeiro endereço utilizável.
func (p Prefixo) PrimeiroHost() ipv4.Endereco {
	if p.Tam >= 31 {
		return p.Base
	}
	return p.Base + 1
}

// UltimoHost devolve o último endereço utilizável.
func (p Prefixo) UltimoHost() ipv4.Endereco {
	if p.Tam >= 31 {
		return p.Broadcast()
	}
	return p.Broadcast() - 1
}

// Contem informa se o endereço pertence ao prefixo.
func (p Prefixo) Contem(ip ipv4.Endereco) bool { return ip&p.Mascara() == p.Base }

// ContemPrefixo informa se q está inteiramente dentro de p (inclusive igual).
func (p Prefixo) ContemPrefixo(q Prefixo) bool { return q.Tam >= p.Tam && p.Contem(q.Base) }

// Sobrepoe informa se os dois prefixos compartilham algum endereço.
func (p Prefixo) Sobrepoe(q Prefixo) bool { return p.ContemPrefixo(q) || q.ContemPrefixo(p) }

// Pai devolve o prefixo imediatamente menos específico. Para /0 devolve ele mesmo.
func (p Prefixo) Pai() Prefixo {
	if p.Tam == 0 {
		return p
	}
	return Novo(p.Base, p.Tam-1)
}

// Divide parte o prefixo em sub-redes de tamanho novoTam, em ordem crescente.
func (p Prefixo) Divide(novoTam int) ([]Prefixo, error) {
	if novoTam < p.Tam || novoTam > 32 {
		return nil, fmt.Errorf("%w: %s -> /%d", ErrTamanho, p, novoTam)
	}
	if novoTam-p.Tam > 20 {
		return nil, fmt.Errorf("%w: divisão gera sub-redes demais", ErrTamanho)
	}
	n := 1 << uint(novoTam-p.Tam)
	passo := uint64(1) << uint(32-novoTam)
	out := make([]Prefixo, n)
	for i := range out {
		out[i] = Prefixo{Base: p.Base + ipv4.Endereco(uint64(i)*passo), Tam: novoTam}
	}
	return out, nil
}

// TamanhoParaHosts devolve o menor prefixo que comporta n hosts utilizáveis
// (mais endereços de rede e broadcast). n deve ser >= 1.
func TamanhoParaHosts(n int) (int, error) {
	if n < 1 {
		return 0, fmt.Errorf("%w: hosts deve ser >= 1", ErrTamanho)
	}
	for tam := 30; tam >= 0; tam-- {
		if (uint64(1)<<uint(32-tam))-2 >= uint64(n) {
			return tam, nil
		}
	}
	return 0, fmt.Errorf("%w: %d hosts não cabem em IPv4", ErrTamanho, n)
}

// VLSM aloca, dentro de rede, uma sub-rede para cada requisito de hosts.
// A alocação é feita do maior para o menor (evita fragmentação), mas o
// resultado preserva a ordem dos requisitos recebidos.
func VLSM(rede Prefixo, hosts []int) ([]Prefixo, error) {
	tams := make([]int, len(hosts))
	for i, h := range hosts {
		t, err := TamanhoParaHosts(h)
		if err != nil {
			return nil, err
		}
		tams[i] = t
	}
	ordem := make([]int, len(hosts))
	for i := range ordem {
		ordem[i] = i
	}
	sort.SliceStable(ordem, func(a, b int) bool { return tams[ordem[a]] < tams[ordem[b]] })

	out := make([]Prefixo, len(hosts))
	proximo := uint64(rede.Base)
	fim := uint64(rede.Broadcast()) + 1
	for _, i := range ordem {
		if tams[i] < rede.Tam {
			return nil, fmt.Errorf("%w: %d hosts não cabem em %s", ErrSemEspaco, hosts[i], rede)
		}
		bloco := uint64(1) << uint(32-tams[i])
		if proximo+bloco > fim {
			return nil, fmt.Errorf("%w: faltou espaço para %d hosts", ErrSemEspaco, hosts[i])
		}
		out[i] = Prefixo{Base: ipv4.Endereco(proximo), Tam: tams[i]}
		proximo += bloco
	}
	return out, nil
}
