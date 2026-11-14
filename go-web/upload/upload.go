// Pacote upload recebe arquivos via multipart/form-data e os guarda em memória.
package upload

import (
	"crypto/sha256"
	"encoding/hex"
	"encoding/json"
	"errors"
	"io"
	"net/http"
	"path/filepath"
	"sync"
)

// Arquivo é um arquivo recebido.
type Arquivo struct {
	Nome     string `json:"nome"`
	Tipo     string `json:"tipo"`
	Tamanho  int    `json:"tamanho"`
	SHA256   string `json:"sha256"`
	conteudo []byte
}

// Armazem guarda arquivos em memória por nome.
type Armazem struct {
	mu       sync.RWMutex
	arquivos map[string]*Arquivo
}

// NovoArmazem cria um armazém vazio.
func NovoArmazem() *Armazem { return &Armazem{arquivos: map[string]*Arquivo{}} }

// Obter devolve o conteúdo do arquivo.
func (a *Armazem) Obter(nome string) ([]byte, bool) {
	a.mu.RLock()
	defer a.mu.RUnlock()
	f, ok := a.arquivos[nome]
	if !ok {
		return nil, false
	}
	return append([]byte(nil), f.conteudo...), true
}

// Config controla o handler.
type Config struct {
	Campo        string   // nome do campo do formulário; padrão "arquivo"
	MaxBytes     int64    // limite do corpo; padrão 1 MiB
	TiposAceitos []string // Content-Type permitidos (vazio = qualquer)
}

// Handler recebe POST multipart e responde 201 com os metadados em JSON.
func (a *Armazem) Handler(c Config) http.Handler {
	if c.Campo == "" {
		c.Campo = "arquivo"
	}
	if c.MaxBytes == 0 {
		c.MaxBytes = 1 << 20
	}
	return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		if r.Method != http.MethodPost {
			http.Error(w, "use POST", http.StatusMethodNotAllowed)
			return
		}
		r.Body = http.MaxBytesReader(w, r.Body, c.MaxBytes)
		if err := r.ParseMultipartForm(c.MaxBytes); err != nil {
			var tg *http.MaxBytesError
			if errors.As(err, &tg) {
				http.Error(w, "arquivo grande demais", http.StatusRequestEntityTooLarge)
				return
			}
			http.Error(w, "formulário multipart inválido", http.StatusBadRequest)
			return
		}
		arq, cab, err := r.FormFile(c.Campo)
		if err != nil {
			http.Error(w, "campo '"+c.Campo+"' ausente", http.StatusBadRequest)
			return
		}
		defer arq.Close()
		tipo := cab.Header.Get("Content-Type")
		if !tipoAceito(c.TiposAceitos, tipo) {
			http.Error(w, "tipo não aceito: "+tipo, http.StatusUnsupportedMediaType)
			return
		}
		dados, err := io.ReadAll(arq)
		if err != nil {
			http.Error(w, "falha ao ler arquivo", http.StatusInternalServerError)
			return
		}
		soma := sha256.Sum256(dados)
		nome := filepath.Base(cab.Filename)
		f := &Arquivo{Nome: nome, Tipo: tipo, Tamanho: len(dados), SHA256: hex.EncodeToString(soma[:]), conteudo: dados}
		a.mu.Lock()
		a.arquivos[nome] = f
		a.mu.Unlock()
		w.Header().Set("Content-Type", "application/json")
		w.WriteHeader(http.StatusCreated)
		json.NewEncoder(w).Encode(f)
	})
}

func tipoAceito(aceitos []string, tipo string) bool {
	if len(aceitos) == 0 {
		return true
	}
	for _, t := range aceitos {
		if t == tipo {
			return true
		}
	}
	return false
}
