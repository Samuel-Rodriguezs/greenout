// Pacote smtp implementa o núcleo de um protocolo de texto estilo SMTP
// (RFC 5321): parser de comandos e uma sessão de servidor orientada a linhas,
// sem qualquer E/S de rede.
package smtp

import (
	"errors"
	"fmt"
	"strings"
)

// MaxLinha é o tamanho máximo de uma linha de comando (RFC 5321, 4.5.3.1.4).
const MaxLinha = 512

// Comando é um comando SMTP já interpretado.
type Comando struct {
	Verbo   string // em maiúsculas: HELO, EHLO, MAIL, RCPT, DATA, RSET, NOOP, QUIT, VRFY
	Arg     string // domínio (HELO/EHLO) ou argumento bruto
	Caminho string // endereço de MAIL FROM / RCPT TO, sem os sinais < >
}

// Erros do parser.
var (
	ErrLinhaLonga   = errors.New("smtp: linha longa demais")
	ErrDesconhecido = errors.New("smtp: comando desconhecido")
	ErrSintaxe      = errors.New("smtp: erro de sintaxe")
)

// ParseComando interpreta uma linha (sem o CRLF final).
func ParseComando(linha string) (Comando, error) {
	if len(linha)+2 > MaxLinha {
		return Comando{}, ErrLinhaLonga
	}
	if strings.ContainsAny(linha, "\r\n\x00") {
		return Comando{}, fmt.Errorf("%w: caractere de controle", ErrSintaxe)
	}
	verbo, resto, _ := strings.Cut(linha, " ")
	verbo = strings.ToUpper(verbo)
	resto = strings.TrimSpace(resto)
	c := Comando{Verbo: verbo, Arg: resto}
	switch verbo {
	case "HELO", "EHLO":
		if resto == "" || strings.ContainsAny(resto, " <>") {
			return Comando{}, fmt.Errorf("%w: %s requer um domínio", ErrSintaxe, verbo)
		}
	case "MAIL", "RCPT":
		prefixo := "FROM:"
		if verbo == "RCPT" {
			prefixo = "TO:"
		}
		if len(resto) < len(prefixo) || !strings.EqualFold(resto[:len(prefixo)], prefixo) {
			return Comando{}, fmt.Errorf("%w: esperava %s", ErrSintaxe, prefixo)
		}
		cam, err := parseCaminho(strings.TrimSpace(resto[len(prefixo):]), verbo == "MAIL")
		if err != nil {
			return Comando{}, err
		}
		c.Caminho = cam
	case "DATA", "RSET", "QUIT":
		if resto != "" {
			return Comando{}, fmt.Errorf("%w: %s não aceita argumentos", ErrSintaxe, verbo)
		}
	case "NOOP":
	case "VRFY":
		if resto == "" {
			return Comando{}, fmt.Errorf("%w: VRFY requer argumento", ErrSintaxe)
		}
	default:
		return Comando{}, fmt.Errorf("%w: %q", ErrDesconhecido, verbo)
	}
	return c, nil
}

// parseCaminho extrai o endereço de "<a@b> [parâmetros]". Se permiteVazio,
// aceita "<>" (remetente nulo de mensagens de retorno).
func parseCaminho(s string, permiteVazio bool) (string, error) {
	if !strings.HasPrefix(s, "<") {
		return "", fmt.Errorf("%w: endereço deve estar entre < >", ErrSintaxe)
	}
	fim := strings.IndexByte(s, '>')
	if fim < 0 {
		return "", fmt.Errorf("%w: faltou >", ErrSintaxe)
	}
	if extra := strings.TrimSpace(s[fim+1:]); extra != "" && strings.ContainsAny(extra, "<>") {
		return "", fmt.Errorf("%w: parâmetros inválidos", ErrSintaxe)
	}
	end := s[1:fim]
	if end == "" {
		if permiteVazio {
			return "", nil
		}
		return "", fmt.Errorf("%w: endereço vazio", ErrSintaxe)
	}
	local, dominio, ok := strings.Cut(end, "@")
	if !ok || local == "" || dominio == "" || strings.ContainsAny(end, " <>@\t") && strings.Count(end, "@") != 1 {
		return "", fmt.Errorf("%w: endereço %q", ErrSintaxe, end)
	}
	if strings.ContainsAny(local, " \t") || strings.ContainsAny(dominio, " \t@") {
		return "", fmt.Errorf("%w: endereço %q", ErrSintaxe, end)
	}
	return end, nil
}

// Resposta é uma resposta SMTP de uma linha.
type Resposta struct {
	Codigo int
	Texto  string
}

func (r Resposta) String() string { return fmt.Sprintf("%d %s", r.Codigo, r.Texto) }

// Mensagem é um e-mail completo recebido por uma sessão.
type Mensagem struct {
	De    string
	Para  []string
	Corpo string // linhas unidas por \n, já sem dot-stuffing
}

type estado int

const (
	inicio estado = iota
	apresentado
	comRemetente
	comDestinatario
	dados
)

// Sessao é o lado servidor de uma conexão SMTP. Não é segura para uso concorrente.
type Sessao struct {
	estado    estado
	de        string
	para      []string
	corpo     []string
	mensagens []Mensagem
	Fechada   bool
}

// Saudacao é a resposta enviada ao abrir a conexão.
func (s *Sessao) Saudacao() Resposta { return Resposta{220, "greenout ESMTP pronto"} }

// Mensagens devolve as mensagens aceitas até o momento.
func (s *Sessao) Mensagens() []Mensagem { return s.mensagens }

func (s *Sessao) reinicia() {
	s.de, s.para, s.corpo = "", nil, nil
	if s.estado != inicio {
		s.estado = apresentado
	}
}

// Processar consome uma linha recebida do cliente e devolve a resposta. No
// modo DATA, as linhas do corpo não geram resposta (ok == false) até o ponto
// final isolado.
func (s *Sessao) Processar(linha string) (r Resposta, ok bool) {
	if s.Fechada {
		return Resposta{421, "conexão encerrada"}, true
	}
	if s.estado == dados {
		return s.linhaDeDados(linha)
	}
	c, err := ParseComando(linha)
	switch {
	case errors.Is(err, ErrLinhaLonga), errors.Is(err, ErrDesconhecido):
		return Resposta{500, "comando não reconhecido"}, true
	case err != nil:
		return Resposta{501, "erro de sintaxe nos parâmetros"}, true
	}
	switch c.Verbo {
	case "HELO", "EHLO":
		s.reinicia()
		s.estado = apresentado
		return Resposta{250, "olá " + c.Arg}, true
	case "MAIL":
		if s.estado == inicio {
			return Resposta{503, "envie HELO/EHLO primeiro"}, true
		}
		if s.estado != apresentado {
			return Resposta{503, "MAIL já informado"}, true
		}
		s.de, s.estado = c.Caminho, comRemetente
		return Resposta{250, "remetente ok"}, true
	case "RCPT":
		if s.estado != comRemetente && s.estado != comDestinatario {
			return Resposta{503, "envie MAIL primeiro"}, true
		}
		s.para = append(s.para, c.Caminho)
		s.estado = comDestinatario
		return Resposta{250, "destinatário ok"}, true
	case "DATA":
		if s.estado != comDestinatario {
			return Resposta{503, "envie RCPT primeiro"}, true
		}
		s.estado = dados
		return Resposta{354, "digite a mensagem, termine com <CRLF>.<CRLF>"}, true
	case "RSET":
		s.reinicia()
		return Resposta{250, "ok"}, true
	case "NOOP":
		return Resposta{250, "ok"}, true
	case "VRFY":
		return Resposta{252, "não verificável, mas aceitarei a mensagem"}, true
	default: // QUIT
		s.Fechada = true
		return Resposta{221, "até logo"}, true
	}
}

func (s *Sessao) linhaDeDados(linha string) (Resposta, bool) {
	if linha == "." {
		s.mensagens = append(s.mensagens, Mensagem{
			De: s.de, Para: s.para, Corpo: strings.Join(s.corpo, "\n"),
		})
		s.reinicia()
		return Resposta{250, "mensagem aceita"}, true
	}
	if strings.HasPrefix(linha, ".") { // remove dot-stuffing
		linha = linha[1:]
	}
	s.corpo = append(s.corpo, linha)
	return Resposta{}, false
}
