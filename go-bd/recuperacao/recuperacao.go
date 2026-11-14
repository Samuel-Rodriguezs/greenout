// Pacote recuperacao implementa um banco chave-valor durável sobre o WAL:
// ao abrir, o log é reproduzido e qualquer final truncado ou corrompido,
// típico de uma queda no meio da escrita, é descartado.
package recuperacao

import (
	"encoding/binary"
	"errors"
	"os"
	"sync"

	"greenout/bd/wal"
)

const (
	opDefinir byte = 1
	opRemover byte = 2
)

// ErrRegistroInvalido indica uma carga de WAL que passou no checksum mas
// não tem o formato esperado.
var ErrRegistroInvalido = errors.New("recuperacao: registro inválido")

// Relatorio descreve o que aconteceu na abertura.
type Relatorio struct {
	Reproduzidos  int   // operações reaplicadas
	BytesPerdidos int64 // bytes descartados do final do log
	Anomalia      error // causa do descarte (wal.ErrTruncado/ErrCorrompido) ou nil
}

// Banco é um KV em memória apoiado por um log.
type Banco struct {
	mu    sync.RWMutex
	dados map[string]string
	log   *wal.Log
}

func codificar(op byte, chave, valor string) []byte {
	b := []byte{op}
	b = binary.AppendUvarint(b, uint64(len(chave)))
	b = append(b, chave...)
	if op == opDefinir {
		b = binary.AppendUvarint(b, uint64(len(valor)))
		b = append(b, valor...)
	}
	return b
}

func decodificar(b []byte) (op byte, chave, valor string, err error) {
	if len(b) < 1 {
		return 0, "", "", ErrRegistroInvalido
	}
	op, b = b[0], b[1:]
	if op != opDefinir && op != opRemover {
		return 0, "", "", ErrRegistroInvalido
	}
	leStr := func() (string, bool) {
		n, k := binary.Uvarint(b)
		if k <= 0 || n > uint64(len(b)-k) {
			return "", false
		}
		s := string(b[k : k+int(n)])
		b = b[k+int(n):]
		return s, true
	}
	var ok bool
	if chave, ok = leStr(); !ok {
		return 0, "", "", ErrRegistroInvalido
	}
	if op == opDefinir {
		if valor, ok = leStr(); !ok {
			return 0, "", "", ErrRegistroInvalido
		}
	}
	if len(b) != 0 {
		return 0, "", "", ErrRegistroInvalido
	}
	return op, chave, valor, nil
}

// Abrir reproduz o log existente, corta o trecho final inválido e devolve o
// banco pronto para novas escritas.
func Abrir(caminho string) (*Banco, Relatorio, error) {
	var rel Relatorio
	dados := map[string]string{}
	res, err := wal.Reproduzir(caminho, func(c []byte) error {
		op, k, v, err := decodificar(c)
		if err != nil {
			return err
		}
		if op == opDefinir {
			dados[k] = v
		} else {
			delete(dados, k)
		}
		return nil
	})
	if errors.Is(err, os.ErrNotExist) {
		res, err = wal.Resultado{}, nil
	}
	if err != nil {
		return nil, rel, err
	}
	rel.Reproduzidos = res.Registros
	rel.Anomalia = res.Anomalia
	if res.Anomalia != nil {
		rel.BytesPerdidos = res.Tamanho - res.OffsetValido
		if err := os.Truncate(caminho, res.OffsetValido); err != nil {
			return nil, rel, err
		}
	}
	l, err := wal.Abrir(caminho)
	if err != nil {
		return nil, rel, err
	}
	return &Banco{dados: dados, log: l}, rel, nil
}

// Definir registra no log e depois aplica na memória.
func (b *Banco) Definir(chave, valor string) error {
	b.mu.Lock()
	defer b.mu.Unlock()
	if err := b.log.Anexar(codificar(opDefinir, chave, valor)); err != nil {
		return err
	}
	b.dados[chave] = valor
	return nil
}

// Remover registra a remoção no log e aplica na memória.
func (b *Banco) Remover(chave string) error {
	b.mu.Lock()
	defer b.mu.Unlock()
	if err := b.log.Anexar(codificar(opRemover, chave, "")); err != nil {
		return err
	}
	delete(b.dados, chave)
	return nil
}

// Obter lê o valor atual.
func (b *Banco) Obter(chave string) (string, bool) {
	b.mu.RLock()
	defer b.mu.RUnlock()
	v, ok := b.dados[chave]
	return v, ok
}

// Tamanho devolve o número de chaves.
func (b *Banco) Tamanho() int {
	b.mu.RLock()
	defer b.mu.RUnlock()
	return len(b.dados)
}

// Fechar sincroniza e fecha o log.
func (b *Banco) Fechar() error {
	b.mu.Lock()
	defer b.mu.Unlock()
	if err := b.log.Sincronizar(); err != nil {
		return err
	}
	return b.log.Fechar()
}
