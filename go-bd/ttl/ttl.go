// Pacote ttl implementa um armazenamento chave-valor com expiração. O
// relógio é injetável (interface Relogio), o que torna a expiração
// testável sem esperar. Chaves expiradas somem na leitura (expiração
// preguiçosa) e também em Varrer (expiração ativa).
package ttl

import (
	"errors"
	"sync"
	"time"
)

// ErrTTLInvalido indica duração negativa.
var ErrTTLInvalido = errors.New("ttl: duração negativa")

// Relogio fornece a hora atual.
type Relogio interface {
	Agora() time.Time
}

// RelogioReal usa time.Now.
type RelogioReal struct{}

// Agora implementa Relogio.
func (RelogioReal) Agora() time.Time { return time.Now() }

// RelogioFalso é um relógio controlado manualmente.
type RelogioFalso struct {
	mu sync.Mutex
	t  time.Time
}

// NovoRelogioFalso cria um relógio parado em t.
func NovoRelogioFalso(t time.Time) *RelogioFalso { return &RelogioFalso{t: t} }

// Agora implementa Relogio.
func (r *RelogioFalso) Agora() time.Time {
	r.mu.Lock()
	defer r.mu.Unlock()
	return r.t
}

// Avancar move o relógio para frente (ou para trás, se d for negativo).
func (r *RelogioFalso) Avancar(d time.Duration) {
	r.mu.Lock()
	r.t = r.t.Add(d)
	r.mu.Unlock()
}

type item struct {
	valor  string
	expira time.Time // zero = não expira
}

// Loja é o armazenamento com TTL.
type Loja struct {
	mu    sync.Mutex
	rel   Relogio
	dados map[string]item
}

// Nova cria uma loja usando o relógio dado (nil usa o relógio real).
func Nova(rel Relogio) *Loja {
	if rel == nil {
		rel = RelogioReal{}
	}
	return &Loja{rel: rel, dados: map[string]item{}}
}

// expirado: no instante exato da expiração a chave já é considerada vencida.
func (l *Loja) expirado(it item, agora time.Time) bool {
	return !it.expira.IsZero() && !agora.Before(it.expira)
}

// vivo devolve o item se existir e não estiver vencido, apagando-o se vencido.
// l.mu deve estar travado.
func (l *Loja) vivo(chave string) (item, bool) {
	it, ok := l.dados[chave]
	if !ok {
		return item{}, false
	}
	if l.expirado(it, l.rel.Agora()) {
		delete(l.dados, chave)
		return item{}, false
	}
	return it, true
}

// Definir grava a chave; ttl == 0 significa sem expiração.
func (l *Loja) Definir(chave, valor string, ttl time.Duration) error {
	if ttl < 0 {
		return ErrTTLInvalido
	}
	l.mu.Lock()
	defer l.mu.Unlock()
	it := item{valor: valor}
	if ttl > 0 {
		it.expira = l.rel.Agora().Add(ttl)
	}
	l.dados[chave] = it
	return nil
}

// Obter devolve o valor se a chave existe e não expirou.
func (l *Loja) Obter(chave string) (string, bool) {
	l.mu.Lock()
	defer l.mu.Unlock()
	it, ok := l.vivo(chave)
	return it.valor, ok
}

// TTL informa o tempo restante. existe=false se a chave não existe ou expirou;
// temTTL=false se existe e nunca expira.
func (l *Loja) TTL(chave string) (restante time.Duration, temTTL, existe bool) {
	l.mu.Lock()
	defer l.mu.Unlock()
	it, ok := l.vivo(chave)
	if !ok {
		return 0, false, false
	}
	if it.expira.IsZero() {
		return 0, false, true
	}
	return it.expira.Sub(l.rel.Agora()), true, true
}

// Expirar define (ou troca) o TTL de uma chave existente; ttl <= 0 apaga a chave.
func (l *Loja) Expirar(chave string, ttl time.Duration) bool {
	l.mu.Lock()
	defer l.mu.Unlock()
	it, ok := l.vivo(chave)
	if !ok {
		return false
	}
	if ttl <= 0 {
		delete(l.dados, chave)
		return true
	}
	it.expira = l.rel.Agora().Add(ttl)
	l.dados[chave] = it
	return true
}

// Persistir remove o TTL; devolve true se havia um TTL a remover.
func (l *Loja) Persistir(chave string) bool {
	l.mu.Lock()
	defer l.mu.Unlock()
	it, ok := l.vivo(chave)
	if !ok || it.expira.IsZero() {
		return false
	}
	it.expira = time.Time{}
	l.dados[chave] = it
	return true
}

// Remover apaga a chave; devolve true se ela estava viva.
func (l *Loja) Remover(chave string) bool {
	l.mu.Lock()
	defer l.mu.Unlock()
	_, ok := l.vivo(chave)
	delete(l.dados, chave)
	return ok
}

// Varrer apaga todas as chaves vencidas e devolve quantas eram.
func (l *Loja) Varrer() int {
	l.mu.Lock()
	defer l.mu.Unlock()
	agora := l.rel.Agora()
	n := 0
	for k, it := range l.dados {
		if l.expirado(it, agora) {
			delete(l.dados, k)
			n++
		}
	}
	return n
}

// Tamanho conta as chaves vivas.
func (l *Loja) Tamanho() int {
	l.mu.Lock()
	defer l.mu.Unlock()
	agora := l.rel.Agora()
	n := 0
	for _, it := range l.dados {
		if !l.expirado(it, agora) {
			n++
		}
	}
	return n
}
