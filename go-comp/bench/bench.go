// Pacote bench oferece programas Mini de carga e utilitários para medir o
// interpretador tree-walking contra a VM de bytecode. Os benchmarks do Go
// ficam em bench_test.go (go test -bench . ./bench).
package bench

import (
	"fmt"
	"strings"
	"time"

	"greenout/comp/codigo"
	"greenout/comp/compilador"
	"greenout/comp/interp"
	"greenout/comp/padrao"
	"greenout/comp/parser"
	"greenout/comp/vm"
)

// Programa é uma carga de trabalho com a saída esperada.
type Programa struct {
	Nome     string
	Fonte    string
	Esperado string
}

// Programas devolve as cargas de trabalho padrão.
func Programas() []Programa {
	return []Programa{
		{"fib-recursivo", `
fn fib(n) { if (n < 2) { return n; } return fib(n - 1) + fib(n - 2); }
print(fib(20));
`, "6765\n"},
		{"soma-laco", `
let i = 0;
let s = 0;
while (i < 100000) { s = s + i; i = i + 1; }
print(s);
`, "4999950000\n"},
		{"crivo", `
fn crivo(n) {
  let primo = [];
  let i = 0;
  while (i <= n) { push(primo, true); i = i + 1; }
  let p = 2;
  let total = 0;
  while (p <= n) {
    if (primo[p]) {
      total = total + 1;
      let m = p * p;
      while (m <= n) { primo[m] = false; m = m + p; }
    }
    p = p + 1;
  }
  return total;
}
print(crivo(5000));
`, "669\n"},
		{"bolha", `
let a = [];
let i = 120;
while (i > 0) { push(a, i); i = i - 1; }
let n = len(a);
let trocou = true;
while (trocou) {
  trocou = false;
  let j = 1;
  while (j < n) {
    if (a[j - 1] > a[j]) { let t = a[j - 1]; a[j - 1] = a[j]; a[j] = t; trocou = true; }
    j = j + 1;
  }
  n = n - 1;
}
print(a[0], a[119]);
`, "1 120\n"},
		{"closures", `
fn contador() { let c = 0; return fn() { c = c + 1; return c; }; }
let f = contador();
let k = 0;
while (k < 9999) { f(); k = k + 1; }
print(f());
`, "10000\n"},
	}
}

// RodarInterp analisa e executa o fonte no interpretador, devolvendo a saída.
func RodarInterp(fonte string) (string, error) {
	prog, es := parser.Analisar(fonte)
	if len(es) > 0 {
		return "", es[0]
	}
	var saida strings.Builder
	in := interp.Novo()
	padrao.Instalar(in, &saida)
	_, err := in.Executar(prog)
	return saida.String(), err
}

// Compilar traduz o fonte para bytecode, para que a medição da VM não
// inclua a análise sintática nem a compilação.
func Compilar(fonte string) (*codigo.Programa, error) {
	prog, es := parser.Analisar(fonte)
	if len(es) > 0 {
		return nil, es[0]
	}
	return compilador.Compilar(prog, padrao.Nomes())
}

// RodarVM executa o bytecode e devolve a saída.
func RodarVM(p *codigo.Programa) (string, error) {
	var saida strings.Builder
	err := vm.Novo(p, padrao.Embutidos(&saida)).Executar()
	return saida.String(), err
}

// Medida compara os tempos médios por execução dos dois executores.
type Medida struct {
	Nome   string
	Interp time.Duration
	VM     time.Duration
}

// Razao devolve quantas vezes a VM é mais rápida que o interpretador
// (maior que 1 significa que a VM venceu).
func (m Medida) Razao() float64 {
	if m.VM <= 0 {
		return 0
	}
	return float64(m.Interp) / float64(m.VM)
}

func (m Medida) String() string {
	return fmt.Sprintf("%-14s interp=%-12v vm=%-12v razão=%.2fx", m.Nome, m.Interp, m.VM, m.Razao())
}

// Comparar executa p repeticoes vezes em cada executor, confere que as saídas
// coincidem com a esperada e devolve os tempos médios.
func Comparar(p Programa, repeticoes int) (Medida, error) {
	if repeticoes < 1 {
		repeticoes = 1
	}
	bc, err := Compilar(p.Fonte)
	if err != nil {
		return Medida{}, err
	}
	m := Medida{Nome: p.Nome}
	inicio := time.Now()
	for i := 0; i < repeticoes; i++ {
		saida, err := RodarInterp(p.Fonte)
		if err != nil {
			return m, fmt.Errorf("interpretador: %w", err)
		}
		if saida != p.Esperado {
			return m, fmt.Errorf("interpretador: saída %q, esperado %q", saida, p.Esperado)
		}
	}
	m.Interp = time.Since(inicio) / time.Duration(repeticoes)
	inicio = time.Now()
	for i := 0; i < repeticoes; i++ {
		saida, err := RodarVM(bc)
		if err != nil {
			return m, fmt.Errorf("vm: %w", err)
		}
		if saida != p.Esperado {
			return m, fmt.Errorf("vm: saída %q, esperado %q", saida, p.Esperado)
		}
	}
	m.VM = time.Since(inicio) / time.Duration(repeticoes)
	return m, nil
}
