// Pacote bloqueio implementa um gerenciador de bloqueios para two-phase
// locking (2PL) com modos compartilhado/exclusivo, promoção (S -> X) e
// detecção de deadlock por ciclo no grafo "espera-por". Ao detectar um
// ciclo, a transação que acabou de pedir o bloqueio é a vítima e recebe
// ErrDeadlock.
//
// Cada transação deve ser usada por uma única goroutine por vez. Não há
// fila justa: um bloqueio é concedido assim que fica compatível com os
// titulares atuais, então leitores contínuos podem atrasar um escritor.
package bloqueio

import (
	"context"
	"errors"
	"sync"
)

// TxID identifica uma transação.
type TxID uint64

// Modo é o tipo de bloqueio.
type Modo int

const (
	// Compartilhado permite vários leitores simultâneos.
	Compartilhado Modo = iota + 1
	// Exclusivo é incompatível com qualquer outro bloqueio.
	Exclusivo
)

func (m Modo) String() string {
	switch m {
	case Compartilhado:
		return "S"
	case Exclusivo:
		return "X"
	}
	return "?"
}

var (
	// ErrDeadlock indica que esperar fecharia um ciclo; a transação deve abortar.
	ErrDeadlock = errors.New("bloqueio: deadlock detectado")
	// ErrFaseEncolhimento indica Adquirir depois de já ter liberado algo (viola 2PL).
	ErrFaseEncolhimento = errors.New("bloqueio: transação já está na fase de liberação")
	// ErrModoInvalido indica modo desconhecido.
	ErrModoInvalido = errors.New("bloqueio: modo inválido")
)

type pedido struct {
	tx        TxID
	modo      Modo
	recurso   string
	pronto    chan struct{}
	concedido bool
}

type recurso struct {
	titulares map[TxID]Modo
	fila      []*pedido
}

// Gerente controla os bloqueios de todos os recursos.
type Gerente struct {
	mu         sync.Mutex
	recursos   map[string]*recurso
	espera     map[TxID]*pedido
	detidos    map[TxID]map[string]struct{}
	encolhendo map[TxID]bool
}

// Novo cria um gerente vazio.
func Novo() *Gerente {
	return &Gerente{
		recursos:   map[string]*recurso{},
		espera:     map[TxID]*pedido{},
		detidos:    map[TxID]map[string]struct{}{},
		encolhendo: map[TxID]bool{},
	}
}

func (g *Gerente) recurso(nome string) *recurso {
	r := g.recursos[nome]
	if r == nil {
		r = &recurso{titulares: map[TxID]Modo{}}
		g.recursos[nome] = r
	}
	return r
}

func (g *Gerente) limpar(nome string, r *recurso) {
	if len(r.titulares) == 0 && len(r.fila) == 0 {
		delete(g.recursos, nome)
	}
}

func conflita(a, b Modo) bool { return a == Exclusivo || b == Exclusivo }

// compativel diz se tx pode obter modo em r dado os demais titulares.
func compativel(r *recurso, tx TxID, modo Modo) bool {
	for t, m := range r.titulares {
		if t != tx && conflita(m, modo) {
			return false
		}
	}
	return true
}

func (g *Gerente) conceder(nome string, r *recurso, tx TxID, modo Modo) {
	if atual, ok := r.titulares[tx]; !ok || modo > atual {
		r.titulares[tx] = modo
	}
	if g.detidos[tx] == nil {
		g.detidos[tx] = map[string]struct{}{}
	}
	g.detidos[tx][nome] = struct{}{}
}

// Adquirir obtém o bloqueio, esperando se necessário. Devolve ErrDeadlock se
// esperar criaria um ciclo, ou o erro do contexto se ele terminar antes.
func (g *Gerente) Adquirir(ctx context.Context, tx TxID, nome string, modo Modo) error {
	if modo != Compartilhado && modo != Exclusivo {
		return ErrModoInvalido
	}
	g.mu.Lock()
	if g.encolhendo[tx] {
		g.mu.Unlock()
		return ErrFaseEncolhimento
	}
	r := g.recurso(nome)
	if atual, ok := r.titulares[tx]; ok && atual >= modo {
		g.mu.Unlock()
		return nil
	}
	if compativel(r, tx, modo) {
		g.conceder(nome, r, tx, modo)
		g.mu.Unlock()
		return nil
	}
	p := &pedido{tx: tx, modo: modo, recurso: nome, pronto: make(chan struct{})}
	r.fila = append(r.fila, p)
	g.espera[tx] = p
	if g.temCiclo(tx) {
		g.cancelar(p)
		g.mu.Unlock()
		return ErrDeadlock
	}
	g.mu.Unlock()

	select {
	case <-p.pronto:
		return nil
	case <-ctx.Done():
		g.mu.Lock()
		defer g.mu.Unlock()
		if p.concedido {
			return nil
		}
		g.cancelar(p)
		return ctx.Err()
	}
}

// cancelar tira um pedido pendente da fila. g.mu deve estar travado.
func (g *Gerente) cancelar(p *pedido) {
	r := g.recursos[p.recurso]
	if r != nil {
		for i, q := range r.fila {
			if q == p {
				r.fila = append(r.fila[:i], r.fila[i+1:]...)
				break
			}
		}
		g.limpar(p.recurso, r)
	}
	if g.espera[p.tx] == p {
		delete(g.espera, p.tx)
	}
}

// bloqueadores lista as transações que impedem o pedido de tx.
func (g *Gerente) bloqueadores(tx TxID) []TxID {
	p := g.espera[tx]
	if p == nil {
		return nil
	}
	var out []TxID
	for t, m := range g.recursos[p.recurso].titulares {
		if t != tx && conflita(m, p.modo) {
			out = append(out, t)
		}
	}
	return out
}

// temCiclo verifica se, a partir de inicio, o grafo espera-por volta a inicio.
func (g *Gerente) temCiclo(inicio TxID) bool {
	visto := map[TxID]bool{}
	var dfs func(t TxID) bool
	dfs = func(t TxID) bool {
		for _, b := range g.bloqueadores(t) {
			if b == inicio {
				return true
			}
			if !visto[b] {
				visto[b] = true
				if dfs(b) {
					return true
				}
			}
		}
		return false
	}
	return dfs(inicio)
}

// concederPendentes acorda os pedidos que se tornaram compatíveis.
func (g *Gerente) concederPendentes(nome string, r *recurso) {
	resto := r.fila[:0]
	for _, p := range r.fila {
		if compativel(r, p.tx, p.modo) {
			g.conceder(nome, r, p.tx, p.modo)
			p.concedido = true
			delete(g.espera, p.tx)
			close(p.pronto)
		} else {
			resto = append(resto, p)
		}
	}
	for i := len(resto); i < len(r.fila); i++ {
		r.fila[i] = nil
	}
	r.fila = resto
}

// Liberar solta um bloqueio individual e coloca a transação na fase de
// encolhimento: novas aquisições passam a falhar até LiberarTudo.
func (g *Gerente) Liberar(tx TxID, nome string) bool {
	g.mu.Lock()
	defer g.mu.Unlock()
	r := g.recursos[nome]
	if r == nil {
		return false
	}
	if _, ok := r.titulares[tx]; !ok {
		return false
	}
	g.encolhendo[tx] = true
	delete(r.titulares, tx)
	delete(g.detidos[tx], nome)
	g.concederPendentes(nome, r)
	g.limpar(nome, r)
	return true
}

// LiberarTudo encerra a transação: solta todos os bloqueios (2PL estrito).
func (g *Gerente) LiberarTudo(tx TxID) {
	g.mu.Lock()
	defer g.mu.Unlock()
	if p := g.espera[tx]; p != nil {
		g.cancelar(p)
	}
	for nome := range g.detidos[tx] {
		r := g.recursos[nome]
		if r == nil {
			continue
		}
		delete(r.titulares, tx)
		g.concederPendentes(nome, r)
		g.limpar(nome, r)
	}
	delete(g.detidos, tx)
	delete(g.encolhendo, tx)
}

// Esperando informa se a transação está bloqueada aguardando algum recurso.
func (g *Gerente) Esperando(tx TxID) bool {
	g.mu.Lock()
	defer g.mu.Unlock()
	return g.espera[tx] != nil
}

// ModoDe devolve o modo em que tx segura o recurso.
func (g *Gerente) ModoDe(tx TxID, nome string) (Modo, bool) {
	g.mu.Lock()
	defer g.mu.Unlock()
	if r := g.recursos[nome]; r != nil {
		m, ok := r.titulares[tx]
		return m, ok
	}
	return 0, false
}

// Recursos devolve quantos recursos têm titulares ou pedidos pendentes.
func (g *Gerente) Recursos() int {
	g.mu.Lock()
	defer g.mu.Unlock()
	return len(g.recursos)
}
