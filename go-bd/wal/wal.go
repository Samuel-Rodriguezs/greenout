// Pacote wal implementa um write-ahead log em arquivo. Cada registro é
// gravado como [tamanho uint32][crc32 uint32][carga] (little endian) e a
// reprodução detecta registros truncados ou corrompidos.
package wal

import (
	"encoding/binary"
	"errors"
	"hash/crc32"
	"io"
	"os"
	"sync"
)

const (
	cabecalho = 8
	// TamanhoMaximo limita o tamanho de uma carga, evitando alocações
	// gigantes quando o campo de tamanho está corrompido.
	TamanhoMaximo = 64 << 20
)

var (
	// ErrTruncado indica que o arquivo termina no meio de um registro.
	ErrTruncado = errors.New("wal: registro truncado")
	// ErrCorrompido indica checksum divergente ou tamanho inválido.
	ErrCorrompido = errors.New("wal: registro corrompido")
	// ErrGrande indica carga acima de TamanhoMaximo.
	ErrGrande = errors.New("wal: carga grande demais")
	// ErrFechado indica uso após Fechar.
	ErrFechado = errors.New("wal: log fechado")
)

var tabela = crc32.MakeTable(crc32.Castagnoli)

// Log é um arquivo de log somente-anexo.
type Log struct {
	mu sync.Mutex
	f  *os.File
}

// Abrir abre (ou cria) o arquivo de log para anexar registros.
func Abrir(caminho string) (*Log, error) {
	f, err := os.OpenFile(caminho, os.O_CREATE|os.O_RDWR|os.O_APPEND, 0o644)
	if err != nil {
		return nil, err
	}
	return &Log{f: f}, nil
}

// Anexar grava um registro no fim do log.
func (l *Log) Anexar(carga []byte) error {
	if len(carga) > TamanhoMaximo {
		return ErrGrande
	}
	buf := make([]byte, cabecalho+len(carga))
	binary.LittleEndian.PutUint32(buf[0:4], uint32(len(carga)))
	binary.LittleEndian.PutUint32(buf[4:8], crc32.Checksum(carga, tabela))
	copy(buf[cabecalho:], carga)

	l.mu.Lock()
	defer l.mu.Unlock()
	if l.f == nil {
		return ErrFechado
	}
	// uma única escrita mantém o registro contíguo
	_, err := l.f.Write(buf)
	return err
}

// Sincronizar força os dados para o disco.
func (l *Log) Sincronizar() error {
	l.mu.Lock()
	defer l.mu.Unlock()
	if l.f == nil {
		return ErrFechado
	}
	return l.f.Sync()
}

// Fechar fecha o arquivo. Chamadas repetidas são inofensivas.
func (l *Log) Fechar() error {
	l.mu.Lock()
	defer l.mu.Unlock()
	if l.f == nil {
		return nil
	}
	err := l.f.Close()
	l.f = nil
	return err
}

// Resultado resume uma reprodução.
type Resultado struct {
	Registros    int   // registros válidos entregues
	OffsetValido int64 // fim do último registro válido
	Tamanho      int64 // tamanho total do arquivo
	Anomalia     error // nil, ErrTruncado ou ErrCorrompido
}

// Reproduzir lê o log do início e chama fn para cada registro íntegro. Para
// no primeiro registro ruim e o descreve em Resultado.Anomalia. Um erro de
// E/S ou devolvido por fn é retornado como error.
func Reproduzir(caminho string, fn func(carga []byte) error) (Resultado, error) {
	var res Resultado
	f, err := os.Open(caminho)
	if err != nil {
		return res, err
	}
	defer f.Close()
	info, err := f.Stat()
	if err != nil {
		return res, err
	}
	res.Tamanho = info.Size()

	var cab [cabecalho]byte
	for {
		_, err := io.ReadFull(f, cab[:])
		if err == io.EOF {
			return res, nil
		}
		if err == io.ErrUnexpectedEOF {
			res.Anomalia = ErrTruncado
			return res, nil
		}
		if err != nil {
			return res, err
		}
		tam := binary.LittleEndian.Uint32(cab[0:4])
		soma := binary.LittleEndian.Uint32(cab[4:8])
		if tam > TamanhoMaximo {
			res.Anomalia = ErrCorrompido
			return res, nil
		}
		if int64(tam) > res.Tamanho-res.OffsetValido-cabecalho {
			res.Anomalia = ErrTruncado
			return res, nil
		}
		carga := make([]byte, tam)
		if _, err := io.ReadFull(f, carga); err != nil {
			if err == io.EOF || err == io.ErrUnexpectedEOF {
				res.Anomalia = ErrTruncado
				return res, nil
			}
			return res, err
		}
		if crc32.Checksum(carga, tabela) != soma {
			res.Anomalia = ErrCorrompido
			return res, nil
		}
		if err := fn(carga); err != nil {
			return res, err
		}
		res.Registros++
		res.OffsetValido += int64(cabecalho) + int64(tam)
	}
}
