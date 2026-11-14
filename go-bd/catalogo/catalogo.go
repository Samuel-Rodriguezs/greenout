// Pacote catalogo mantém o catálogo de tabelas do banco: nomes, esquemas
// (pacote linhas) e chave primária. O catálogo persiste em um arquivo com
// cabeçalho mágico e CRC32, gravado de forma atômica (arquivo temporário
// seguido de rename), e é revalidado por inteiro ao ser carregado.
package catalogo

import (
	"encoding/binary"
	"encoding/json"
	"errors"
	"fmt"
	"hash/crc32"
	"os"
	"regexp"
	"sort"
	"sync"

	"greenout/bd/linhas"
)

var (
	// ErrExiste indica tabela já existente.
	ErrExiste = errors.New("catalogo: tabela já existe")
	// ErrNaoExiste indica tabela inexistente.
	ErrNaoExiste = errors.New("catalogo: tabela não existe")
	// ErrNome indica nome de tabela ou coluna inválido.
	ErrNome = errors.New("catalogo: nome inválido")
	// ErrChavePrimaria indica chave primária inválida.
	ErrChavePrimaria = errors.New("catalogo: chave primária inválida")
	// ErrColunaObrigatoria indica nova coluna não nulável (as linhas antigas não a têm).
	ErrColunaObrigatoria = errors.New("catalogo: coluna nova precisa ser nulável")
	// ErrArquivo indica arquivo de catálogo corrompido.
	ErrArquivo = errors.New("catalogo: arquivo corrompido")
)

const magic = "CAT1"

var reNome = regexp.MustCompile(`^[A-Za-z_][A-Za-z0-9_]{0,62}$`)

// Tabela descreve uma tabela do catálogo.
type Tabela struct {
	Nome          string         `json:"nome"`
	Esquema       linhas.Esquema `json:"esquema"`
	ChavePrimaria string         `json:"chave_primaria,omitempty"`
}

func (t Tabela) copia() Tabela {
	t.Esquema = linhas.Esquema{Colunas: append([]linhas.Coluna(nil), t.Esquema.Colunas...)}
	return t
}

func validarTabela(t Tabela) error {
	if !reNome.MatchString(t.Nome) {
		return fmt.Errorf("%w: tabela %q", ErrNome, t.Nome)
	}
	if err := t.Esquema.Validar(); err != nil {
		return err
	}
	for _, c := range t.Esquema.Colunas {
		if !reNome.MatchString(c.Nome) {
			return fmt.Errorf("%w: coluna %q", ErrNome, c.Nome)
		}
	}
	if t.ChavePrimaria != "" {
		i := t.Esquema.Indice(t.ChavePrimaria)
		if i < 0 {
			return fmt.Errorf("%w: coluna %q não existe", ErrChavePrimaria, t.ChavePrimaria)
		}
		if t.Esquema.Colunas[i].Nulavel {
			return fmt.Errorf("%w: coluna %q é nulável", ErrChavePrimaria, t.ChavePrimaria)
		}
	}
	return nil
}

// Catalogo é o conjunto de tabelas, seguro para uso concorrente.
type Catalogo struct {
	mu      sync.RWMutex
	tabelas map[string]Tabela
}

// Novo cria um catálogo vazio.
func Novo() *Catalogo { return &Catalogo{tabelas: map[string]Tabela{}} }

// Criar registra uma tabela. chavePrimaria pode ser vazia.
func (c *Catalogo) Criar(nome string, esq linhas.Esquema, chavePrimaria string) error {
	t := Tabela{Nome: nome, Esquema: esq, ChavePrimaria: chavePrimaria}.copia()
	if err := validarTabela(t); err != nil {
		return err
	}
	c.mu.Lock()
	defer c.mu.Unlock()
	if _, ok := c.tabelas[nome]; ok {
		return fmt.Errorf("%w: %s", ErrExiste, nome)
	}
	c.tabelas[nome] = t
	return nil
}

// Obter devolve uma cópia da tabela.
func (c *Catalogo) Obter(nome string) (Tabela, bool) {
	c.mu.RLock()
	defer c.mu.RUnlock()
	t, ok := c.tabelas[nome]
	return t.copia(), ok
}

// Remover apaga a tabela.
func (c *Catalogo) Remover(nome string) error {
	c.mu.Lock()
	defer c.mu.Unlock()
	if _, ok := c.tabelas[nome]; !ok {
		return fmt.Errorf("%w: %s", ErrNaoExiste, nome)
	}
	delete(c.tabelas, nome)
	return nil
}

// Renomear troca o nome de uma tabela.
func (c *Catalogo) Renomear(de, para string) error {
	if !reNome.MatchString(para) {
		return fmt.Errorf("%w: tabela %q", ErrNome, para)
	}
	c.mu.Lock()
	defer c.mu.Unlock()
	t, ok := c.tabelas[de]
	if !ok {
		return fmt.Errorf("%w: %s", ErrNaoExiste, de)
	}
	if _, ok := c.tabelas[para]; ok && de != para {
		return fmt.Errorf("%w: %s", ErrExiste, para)
	}
	delete(c.tabelas, de)
	t.Nome = para
	c.tabelas[para] = t
	return nil
}

// AdicionarColuna acrescenta uma coluna ao fim do esquema. Ela precisa ser
// nulável, pois as linhas já gravadas não têm valor para ela.
func (c *Catalogo) AdicionarColuna(tabela string, col linhas.Coluna) error {
	if !col.Nulavel {
		return ErrColunaObrigatoria
	}
	c.mu.Lock()
	defer c.mu.Unlock()
	t, ok := c.tabelas[tabela]
	if !ok {
		return fmt.Errorf("%w: %s", ErrNaoExiste, tabela)
	}
	t = t.copia()
	t.Esquema.Colunas = append(t.Esquema.Colunas, col)
	if err := validarTabela(t); err != nil {
		return err
	}
	c.tabelas[tabela] = t
	return nil
}

// Listar devolve os nomes das tabelas em ordem alfabética.
func (c *Catalogo) Listar() []string {
	c.mu.RLock()
	defer c.mu.RUnlock()
	ns := make([]string, 0, len(c.tabelas))
	for n := range c.tabelas {
		ns = append(ns, n)
	}
	sort.Strings(ns)
	return ns
}

// Salvar grava o catálogo no caminho, de forma atômica.
func (c *Catalogo) Salvar(caminho string) error {
	c.mu.RLock()
	lista := make([]Tabela, 0, len(c.tabelas))
	for _, t := range c.tabelas {
		lista = append(lista, t)
	}
	c.mu.RUnlock()
	sort.Slice(lista, func(i, j int) bool { return lista[i].Nome < lista[j].Nome })
	corpo, err := json.Marshal(lista)
	if err != nil {
		return err
	}
	buf := append([]byte(magic), 0, 0, 0, 0)
	binary.LittleEndian.PutUint32(buf[4:], crc32.ChecksumIEEE(corpo))
	buf = append(buf, corpo...)

	tmp := caminho + ".tmp"
	if err := os.WriteFile(tmp, buf, 0o644); err != nil {
		return err
	}
	if err := os.Rename(tmp, caminho); err != nil {
		os.Remove(tmp)
		return err
	}
	return nil
}

// Carregar lê um catálogo salvo, validando cabeçalho, CRC e cada tabela.
func Carregar(caminho string) (*Catalogo, error) {
	b, err := os.ReadFile(caminho)
	if err != nil {
		return nil, err
	}
	if len(b) < 8 || string(b[:4]) != magic {
		return nil, fmt.Errorf("%w: cabeçalho inválido", ErrArquivo)
	}
	corpo := b[8:]
	if binary.LittleEndian.Uint32(b[4:8]) != crc32.ChecksumIEEE(corpo) {
		return nil, fmt.Errorf("%w: checksum divergente", ErrArquivo)
	}
	var lista []Tabela
	if err := json.Unmarshal(corpo, &lista); err != nil {
		return nil, fmt.Errorf("%w: %v", ErrArquivo, err)
	}
	c := Novo()
	for _, t := range lista {
		if err := validarTabela(t); err != nil {
			return nil, fmt.Errorf("%w: %v", ErrArquivo, err)
		}
		if _, dup := c.tabelas[t.Nome]; dup {
			return nil, fmt.Errorf("%w: tabela %q repetida", ErrArquivo, t.Nome)
		}
		c.tabelas[t.Nome] = t
	}
	return c, nil
}
