package dns

import (
	"bytes"
	"encoding/hex"
	"errors"
	"reflect"
	"testing"
)

func hexb(t *testing.T, s string) []byte {
	t.Helper()
	b, err := hex.DecodeString(s)
	if err != nil {
		t.Fatal(err)
	}
	return b
}

// Consulta A para example.com com RD=1 e resposta com ponteiro de compressão.
const (
	consultaHex = "123401000001000000000000" + "076578616d706c6503636f6d00" + "00010001"
	respostaHex = "12348180000100010000000007" + "6578616d706c6503636f6d00" + "00010001" +
		"c00c" + "0001" + "0001" + "0000012c" + "0004" + "5db8d822"
)

func TestParseConsulta(t *testing.T) {
	m, err := Parse(hexb(t, consultaHex))
	if err != nil {
		t.Fatal(err)
	}
	c := m.Cabecalho
	if c.ID != 0x1234 || c.Resposta || !c.RD || c.QD != 1 || c.AN != 0 {
		t.Errorf("cabeçalho = %+v", c)
	}
	if !reflect.DeepEqual(m.Perguntas, []Pergunta{{"example.com", TipoA, ClasseIN}}) {
		t.Errorf("perguntas = %+v", m.Perguntas)
	}
}

func TestParseRespostaComPonteiro(t *testing.T) {
	m, err := Parse(hexb(t, respostaHex))
	if err != nil {
		t.Fatal(err)
	}
	c := m.Cabecalho
	if !c.Resposta || !c.RD || !c.RA || c.AA || c.Rcode != 0 || c.AN != 1 {
		t.Errorf("cabeçalho = %+v", c)
	}
	if len(m.Respostas) != 1 {
		t.Fatalf("respostas = %d", len(m.Respostas))
	}
	r := m.Respostas[0]
	if r.Nome != "example.com" || r.Tipo != TipoA || r.TTL != 300 || r.Texto != "93.184.216.34" ||
		!bytes.Equal(r.Dados, []byte{0x5d, 0xb8, 0xd8, 0x22}) {
		t.Errorf("registro = %+v", r)
	}
}

func TestLerNomeCompressao(t *testing.T) {
	// Offset 0: "www.exemplo.com"; offset 17: "mail" + ponteiro para "exemplo.com" (off 4);
	// offset 24: ponteiro encadeado para o nome em 17.
	msg := []byte{3, 'w', 'w', 'w', 7, 'e', 'x', 'e', 'm', 'p', 'l', 'o', 3, 'c', 'o', 'm', 0,
		4, 'm', 'a', 'i', 'l', 0xC0, 0x04,
		0xC0, 17}
	casos := []struct {
		off  int
		nome string
		prox int
	}{
		{0, "www.exemplo.com", 17},
		{17, "mail.exemplo.com", 24},
		{24, "mail.exemplo.com", 26},
		{4, "exemplo.com", 17},
	}
	for _, c := range casos {
		nome, prox, err := LerNome(msg, c.off)
		if err != nil || nome != c.nome || prox != c.prox {
			t.Errorf("LerNome(%d) = %q,%d,%v; esperava %q,%d", c.off, nome, prox, err, c.nome, c.prox)
		}
	}
	if n, p, err := LerNome([]byte{0}, 0); err != nil || n != "." || p != 1 {
		t.Errorf("raiz: %q %d %v", n, p, err)
	}
}

func TestLerNomeInvalido(t *testing.T) {
	longo := bytes.Repeat(append([]byte{63}, bytes.Repeat([]byte("a"), 63)...), 4)
	longo = append(longo, 0)
	casos := []struct {
		nome string
		msg  []byte
		off  int
		erro error
	}{
		{"fora", []byte{}, 0, ErrCurto},
		{"rótulo truncado", []byte{5, 'a', 'b'}, 0, ErrCurto},
		{"sem terminador", []byte{1, 'a'}, 0, ErrCurto},
		{"ponteiro truncado", []byte{0xC0}, 0, ErrCurto},
		{"ponteiro para si", []byte{0xC0, 0x00}, 0, ErrPonteiro},
		{"ponteiro para frente", []byte{0xC0, 0x05, 0, 0, 0, 0}, 0, ErrPonteiro},
		{"rótulo reservado 0x40", []byte{0x41, 'a', 0}, 0, ErrRotulo},
		{"rótulo reservado 0x80", []byte{0x81, 'a', 0}, 0, ErrRotulo},
		{"nome > 255", longo, 0, ErrNomeLongo},
	}
	for _, c := range casos {
		if _, _, err := LerNome(c.msg, c.off); !errors.Is(err, c.erro) {
			t.Errorf("%s: err=%v, esperava %v", c.nome, err, c.erro)
		}
	}
}

// Ponteiros só voltam no buffer, então um laço A->B->A é impossível; o nome
// deve ainda assim terminar e ter limite.
func TestLerNomeLaco(t *testing.T) {
	// Em 0: rótulo "a" seguido de ponteiro para 0 (alvo == pos? pos do ponteiro é 2, alvo 0 < 2).
	// Seguir o ponteiro repete o rótulo "a" indefinidamente: deve parar por ErrNomeLongo.
	msg := []byte{1, 'a', 0xC0, 0x00}
	if _, _, err := LerNome(msg, 0); !errors.Is(err, ErrNomeLongo) {
		t.Errorf("laço deveria estourar o limite de nome: %v", err)
	}
}

func TestParseMalformado(t *testing.T) {
	bom := hexb(t, respostaHex)
	casos := []struct {
		nome string
		msg  []byte
	}{
		{"vazio", nil},
		{"cabeçalho curto", bom[:11]},
		{"pergunta cortada", bom[:20]},
		{"sem tipo/classe", bom[:12+13]},
		{"registro cortado", bom[:len(bom)-2]},
		{"rdlength excessivo", func() []byte { b := append([]byte(nil), bom...); b[len(b)-5] = 0xFF; return b }()},
	}
	for _, c := range casos {
		if _, err := Parse(c.msg); !errors.Is(err, ErrCurto) {
			t.Errorf("%s: err=%v", c.nome, err)
		}
	}
	// Contagem de perguntas maior que o conteúdo.
	b := append([]byte(nil), hexb(t, consultaHex)...)
	b[5] = 9
	if _, err := Parse(b); err == nil {
		t.Error("QD inflado deveria falhar")
	}
}

func TestSerializarComCompressao(t *testing.T) {
	m := Mensagem{
		Cabecalho: Cabecalho{ID: 0xABCD, Resposta: true, RD: true, RA: true, Opcode: 0, Rcode: 3, AA: true},
		Perguntas: []Pergunta{{"www.example.com", TipoA, ClasseIN}},
		Respostas: []Registro{
			{Nome: "www.example.com", Tipo: TipoCNAME, Classe: ClasseIN, TTL: 60, Texto: "web.example.com"},
			{Nome: "web.example.com", Tipo: TipoA, Classe: ClasseIN, TTL: 30, Dados: []byte{10, 0, 0, 7}},
		},
		Autoridades: []Registro{{Nome: "example.com", Tipo: TipoNS, Classe: ClasseIN, TTL: 3600, Texto: "ns1.example.com"}},
	}
	b, err := m.Serializar()
	if err != nil {
		t.Fatal(err)
	}
	// Sem compressão os nomes ocupariam bem mais; "example.com" aparece uma vez.
	if n := bytes.Count(b, []byte("example")); n != 1 {
		t.Errorf("'example' aparece %d vezes; compressão ineficaz", n)
	}
	got, err := Parse(b)
	if err != nil {
		t.Fatal(err)
	}
	m.Cabecalho.QD, m.Cabecalho.AN, m.Cabecalho.NS = 1, 2, 1
	if got.Cabecalho != m.Cabecalho {
		t.Errorf("cabeçalho %+v != %+v", got.Cabecalho, m.Cabecalho)
	}
	if !reflect.DeepEqual(got.Perguntas, m.Perguntas) {
		t.Errorf("perguntas %+v", got.Perguntas)
	}
	if got.Respostas[0].Texto != "web.example.com" || got.Respostas[0].Nome != "www.example.com" ||
		got.Respostas[1].Texto != "10.0.0.7" || got.Respostas[1].Nome != "web.example.com" ||
		got.Autoridades[0].Texto != "ns1.example.com" || got.Autoridades[0].TTL != 3600 {
		t.Errorf("registros: %+v %+v", got.Respostas, got.Autoridades)
	}
}

func TestSerializarReproduzConsulta(t *testing.T) {
	m := Mensagem{Cabecalho: Cabecalho{ID: 0x1234, RD: true}, Perguntas: []Pergunta{{"example.com", TipoA, ClasseIN}}}
	b, err := m.Serializar()
	if err != nil || hex.EncodeToString(b) != consultaHex {
		t.Errorf("bytes = %x err=%v", b, err)
	}
}

func TestSerializarNomesInvalidos(t *testing.T) {
	for _, n := range []string{"a..b", ".a", string(bytes.Repeat([]byte("x"), 64)) + ".com"} {
		m := Mensagem{Perguntas: []Pergunta{{n, TipoA, ClasseIN}}}
		if _, err := m.Serializar(); !errors.Is(err, ErrRotulo) {
			t.Errorf("nome %q: err=%v", n, err)
		}
	}
	// Raiz é válida.
	b, err := Mensagem{Perguntas: []Pergunta{{".", TipoNS, ClasseIN}}}.Serializar()
	if err != nil || b[12] != 0 {
		t.Errorf("raiz: %x %v", b, err)
	}
}

func TestFlagsIdaEVolta(t *testing.T) {
	for _, c := range []Cabecalho{
		{ID: 1, Resposta: true, Opcode: 2, AA: true, TC: true, RD: true, RA: true, Rcode: 5},
		{ID: 2},
		{ID: 3, Opcode: 15, Rcode: 15},
	} {
		b, _ := Mensagem{Cabecalho: c}.Serializar()
		m, err := Parse(b)
		if err != nil || m.Cabecalho != c {
			t.Errorf("%+v -> %+v (%v)", c, m.Cabecalho, err)
		}
	}
}
