package e2e

import (
	"fmt"
	"sort"
	"strings"
	"testing"

	"greenout/comp/erros"
)

// modos são as quatro formas de executar o mesmo programa; todas devem
// produzir exatamente a mesma saída.
var modos = []struct {
	nome      string
	vm, otimi bool
}{
	{"interp", false, false},
	{"vm", true, false},
	{"interp+otimizado", false, true},
	{"vm+otimizado", true, true},
}

// verificar roda o programa nos quatro modos e compara com a saída esperada.
func verificar(t *testing.T, fonte, quer string) {
	t.Helper()
	for _, m := range modos {
		r := Executar(fonte, m.vm, m.otimi)
		if r.Falha != nil {
			t.Errorf("[%s] falha inesperada: %v\n%s", m.nome, r.Falha, r.Falha.Diagnostico)
			continue
		}
		if r.Saida != quer {
			t.Errorf("[%s] saída diferente.\n got:\n%s\nquer:\n%s", m.nome, r.Saida, quer)
		}
	}
}

func formatarArray(xs []int) string {
	partes := make([]string, len(xs))
	for i, x := range xs {
		partes[i] = fmt.Sprint(x)
	}
	return "[" + strings.Join(partes, ", ") + "]"
}

const progFatorial = `
fn fat(n) {
  if (n <= 1) { return 1; }
  return n * fat(n - 1);
}
let i = 0;
while (i <= 15) {
  print(i, fat(i));
  i = i + 1;
}
`

func TestFatorial(t *testing.T) {
	var sb strings.Builder
	f := 1
	for i := 0; i <= 15; i++ {
		if i > 1 {
			f *= i
		}
		fmt.Fprintf(&sb, "%d %d\n", i, f)
	}
	verificar(t, progFatorial, sb.String())
}

const progFibonacci = `
fn fib(n) {
  if (n < 2) { return n; }
  return fib(n - 1) + fib(n - 2);
}
fn fibIter(n) {
  let a = 0;
  let b = 1;
  let i = 0;
  while (i < n) {
    let t = a + b;
    a = b;
    b = t;
    i = i + 1;
  }
  return a;
}
let i = 0;
let divergencias = 0;
while (i <= 20) {
  if (fib(i) != fibIter(i)) { divergencias = divergencias + 1; }
  i = i + 1;
}
print("divergencias:", divergencias);
print(fib(20), fibIter(80));
`

func TestFibonacci(t *testing.T) {
	a, b := 0, 1
	var f80 int
	for i := 0; i <= 80; i++ {
		if i == 80 {
			f80 = a
		}
		a, b = b, a+b
	}
	verificar(t, progFibonacci, fmt.Sprintf("divergencias: 0\n6765 %d\n", f80))
}

const progCrivo = `
fn crivo(n) {
  let primo = [];
  let i = 0;
  while (i <= n) { push(primo, true); i = i + 1; }
  primo[0] = false;
  primo[1] = false;
  let p = 2;
  while (p * p <= n) {
    if (primo[p]) {
      let m = p * p;
      while (m <= n) { primo[m] = false; m = m + p; }
    }
    p = p + 1;
  }
  let res = [];
  let k = 0;
  while (k <= n) {
    if (primo[k]) { push(res, k); }
    k = k + 1;
  }
  return res;
}
print(crivo(100));
print(len(crivo(2000)));
`

func primosAte(n int) []int {
	comp := make([]bool, n+1)
	var res []int
	for i := 2; i <= n; i++ {
		if !comp[i] {
			res = append(res, i)
			for m := i * i; m <= n; m += i {
				comp[m] = true
			}
		}
	}
	return res
}

func TestCrivo(t *testing.T) {
	quer := fmt.Sprintf("%s\n%d\n", formatarArray(primosAte(100)), len(primosAte(2000)))
	verificar(t, progCrivo, quer)
}

const progOrdenacao = `
let semente = 42;
fn proximo() {
  semente = (semente * 1103515245 + 12345) % 2147483648;
  return semente;
}
fn gerar(n) {
  let xs = [];
  let i = 0;
  while (i < n) { push(xs, proximo() % 1000); i = i + 1; }
  return xs;
}
fn copia(a) {
  let r = [];
  let i = 0;
  while (i < len(a)) { push(r, a[i]); i = i + 1; }
  return r;
}
fn bolha(a) {
  let n = len(a);
  let trocou = true;
  while (trocou) {
    trocou = false;
    let i = 1;
    while (i < n) {
      if (a[i - 1] > a[i]) {
        let t = a[i - 1];
        a[i - 1] = a[i];
        a[i] = t;
        trocou = true;
      }
      i = i + 1;
    }
    n = n - 1;
  }
  return a;
}
fn insercao(a) {
  let i = 1;
  while (i < len(a)) {
    let chave = a[i];
    let j = i - 1;
    while (j >= 0 && a[j] > chave) { a[j + 1] = a[j]; j = j - 1; }
    a[j + 1] = chave;
    i = i + 1;
  }
  return a;
}
fn qs(a) {
  if (len(a) <= 1) { return a; }
  let pivo = a[0];
  let menores = [];
  let maiores = [];
  let i = 1;
  while (i < len(a)) {
    if (a[i] < pivo) { push(menores, a[i]); } else { push(maiores, a[i]); }
    i = i + 1;
  }
  let r = qs(menores);
  push(r, pivo);
  let m = qs(maiores);
  let j = 0;
  while (j < len(m)) { push(r, m[j]); j = j + 1; }
  return r;
}
let dados = gerar(40);
print(dados);
let b = bolha(copia(dados));
print(b);
print(b == insercao(copia(dados)), b == qs(dados));
`

func TestOrdenacao(t *testing.T) {
	semente := 42
	dados := make([]int, 40)
	for i := range dados {
		semente = (semente*1103515245 + 12345) % 2147483648
		dados[i] = semente % 1000
	}
	ord := append([]int(nil), dados...)
	sort.Ints(ord)
	quer := fmt.Sprintf("%s\n%s\ntrue true\n", formatarArray(dados), formatarArray(ord))
	verificar(t, progOrdenacao, quer)
}

func TestTextos(t *testing.T) {
	fonte := `
fn inverte(s) {
  let r = "";
  let i = len(s) - 1;
  while (i >= 0) { r = r + s[i]; i = i - 1; }
  return r;
}
fn palindromo(s) { return s == inverte(s); }
print(inverte("mini"), palindromo("arara"), palindromo("mini"));
let linha = "";
let i = 0;
while (i < 3) { linha = linha + "ab"; i = i + 1; }
print(linha, len(linha), "x" < "y", "linha\ncom\tescapes \"e\" \\");
`
	verificar(t, fonte, "inim true false\nababab 6 true linha\ncom\tescapes \"e\" \\\n")
}

func TestClosuresEOrdemSuperior(t *testing.T) {
	fonte := `
fn contador() {
  let c = 0;
  return fn() { c = c + 1; return c; };
}
let a = contador();
let b = contador();
print(a(), a(), a(), b());

fn mapear(xs, f) {
  let r = [];
  let i = 0;
  while (i < len(xs)) { push(r, f(xs[i])); i = i + 1; }
  return r;
}
fn filtrar(xs, p) {
  let r = [];
  let i = 0;
  while (i < len(xs)) { if (p(xs[i])) { push(r, xs[i]); } i = i + 1; }
  return r;
}
fn reduzir(xs, f, acc) {
  let i = 0;
  while (i < len(xs)) { acc = f(acc, xs[i]); i = i + 1; }
  return acc;
}
let nums = [1, 2, 3, 4, 5, 6];
let quad = mapear(nums, fn(x) { return x * x; });
let pares = filtrar(quad, fn(x) { return x % 2 == 0; });
print(quad, pares, reduzir(quad, fn(s, x) { return s + x; }, 0));

fn compor(f, g) { return fn(x) { return f(g(x)); }; }
let maisUmDobro = compor(fn(x) { return x * 2; }, fn(x) { return x + 1; });
print(maisUmDobro(5));

let fs = [];
let k = 0;
while (k < 3) { let capturado = k * 10; push(fs, fn() { return capturado; }); k = k + 1; }
print(fs[0](), fs[1](), fs[2]());
`
	verificar(t, fonte, "1 2 3 1\n[1, 4, 9, 16, 25, 36] [4, 16, 36] 91\n12\n0 10 20\n")
}

func TestAlgoritmosClassicos(t *testing.T) {
	fonte := `
fn mdc(a, b) { if (b == 0) { return a; } return mdc(b, a % b); }
fn collatz(n) {
  let passos = 0;
  while (n != 1) {
    if (n % 2 == 0) { n = n / 2; } else { n = 3 * n + 1; }
    passos = passos + 1;
  }
  return passos;
}
fn hanoi(n) { if (n == 0) { return 0; } return 2 * hanoi(n - 1) + 1; }
fn potmod(b, e, m) {
  let r = 1;
  b = b % m;
  while (e > 0) {
    if (e % 2 == 1) { r = r * b % m; }
    e = e / 2;
    b = b * b % m;
  }
  return r;
}
fn par(n) { if (n == 0) { return true; } return impar(n - 1); }
fn impar(n) { if (n == 0) { return false; } return par(n - 1); }
print(mdc(1071, 462), collatz(27), hanoi(10), potmod(2, 100, 1000007), par(10), impar(7));
`
	// potmod(2,100,1000007) calculado em Go abaixo
	r := 1
	b := 2
	for e := 100; e > 0; e /= 2 {
		if e%2 == 1 {
			r = r * b % 1000007
		}
		b = b * b % 1000007
	}
	passos, n := 0, 27
	for n != 1 {
		if n%2 == 0 {
			n /= 2
		} else {
			n = 3*n + 1
		}
		passos++
	}
	verificar(t, fonte, fmt.Sprintf("21 %d 1023 %d true true\n", passos, r))
}

func TestMatrizes(t *testing.T) {
	fonte := `
fn mul(a, b) {
  return [
    [a[0][0] * b[0][0] + a[0][1] * b[1][0], a[0][0] * b[0][1] + a[0][1] * b[1][1]],
    [a[1][0] * b[0][0] + a[1][1] * b[1][0], a[1][0] * b[0][1] + a[1][1] * b[1][1]]
  ];
}
fn fibMatriz(n) {
  let r = [[1, 0], [0, 1]];
  let b = [[1, 1], [1, 0]];
  while (n > 0) {
    if (n % 2 == 1) { r = mul(r, b); }
    b = mul(b, b);
    n = n / 2;
  }
  return r[0][1];
}
print(fibMatriz(10), fibMatriz(50), fibMatriz(80));
`
	verificar(t, fonte, "55 12586269025 23416728348467685\n")
}

func TestDeclaracaoIcadaUsandoVariavelGlobal(t *testing.T) {
	fonte := `
let base = 10;
fn soma(x) { return x + base; }
print(soma(1));
base = 20;
print(soma(1), dobro(4));
fn dobro(n) { return n * 2; }
`
	verificar(t, fonte, "11\n21 8\n")
}

func TestDeclarativosEEstadoLocal(t *testing.T) {
	fonte := `
let x = 1;
{
  let x = x + 10;
  print(x);
  { let x = x * 2; print(x); }
  print(x);
}
print(x);
fn f() { let x = 100; return x; }
print(f(), x);
`
	verificar(t, fonte, "11\n22\n11\n1\n100 1\n")
}

// A otimização deve acontecer de fato e não alterar o resultado.
func TestOtimizacoes(t *testing.T) {
	fonte := `
let n = 2 * 3 + 4;
if (1 < 2) { print("sim", n); } else { print("nao"); }
while (false) { print("nunca"); }
fn f() { return 10 - 3; print("morto"); }
print(f());
`
	_, est, falha := Preparar(fonte, true)
	if falha != nil {
		t.Fatal(falha)
	}
	if est.Dobras != 4 || est.Removidos < 4 {
		t.Errorf("estatísticas = %+v", est)
	}
	_, est, _ = Preparar(fonte, false)
	if est != (Estatisticas{}) {
		t.Errorf("sem otimizar não deveria haver estatísticas: %+v", est)
	}
	verificar(t, fonte, "sim 10\n7\n")
}

func TestFalhasEstaticas(t *testing.T) {
	casos := []struct {
		nome    string
		fonte   string
		fase    erros.Fase
		msg     string
		trechos []string
	}{
		{"sintaxe", "let x = ;", erros.Sintaxe, "1:9: expressão esperada, encontrado ';'", []string{"erro[sintaxe]", "1 | let x = ;", "  |         ^"}},
		{"semantica", "let a = 1;\nprint(b);", erros.Semantica, "2:7: variável 'b' não declarada", []string{"erro[semântica]", "2 | print(b);"}},
		{"tipos", "let x = 1 + \"a\";", erros.Tipos, "1:11: operador '+' requer dois int ou dois texto, recebeu int e texto", []string{"erro[tipos]"}},
		{"retorno fora de funcao", "return 1;", erros.Semantica, "1:1: 'return' fora de função", nil},
		{"aridade conhecida", "fn f(a) { return a; }\nf(1, 2);", erros.Tipos, "2:2: 'f' espera 1 argumento(s), recebeu 2", nil},
		{"condicao nao bool", "if (1) { }", erros.Tipos, "1:5: condição deve ser bool, recebeu int", nil},
	}
	for _, c := range casos {
		t.Run(c.nome, func(t *testing.T) {
			for _, m := range modos {
				r := Executar(c.fonte, m.vm, m.otimi)
				if r.Falha == nil {
					t.Fatalf("[%s] esperado falha", m.nome)
				}
				if r.Falha.Fase != c.fase || r.Falha.Err.Error() != c.msg {
					t.Errorf("[%s] falha = %s %q, quer %s %q", m.nome, r.Falha.Fase, r.Falha.Err, c.fase, c.msg)
				}
				for _, tr := range c.trechos {
					if !strings.Contains(r.Falha.Diagnostico, tr) {
						t.Errorf("[%s] diagnóstico deveria conter %q:\n%s", m.nome, tr, r.Falha.Diagnostico)
					}
				}
				if r.Saida != "" {
					t.Errorf("[%s] nada deveria ter sido executado, saída %q", m.nome, r.Saida)
				}
			}
		})
	}
}

// Erros de execução devem ter a mesma mensagem e posição no interpretador e na VM,
// e a saída produzida antes do erro deve ser preservada.
func TestFalhasDeExecucao(t *testing.T) {
	casos := []struct {
		nome  string
		fonte string
		saida string
		msg   string
	}{
		{"divisao por zero", "print(\"antes\");\nfn f(a, b) { return a / b; }\nprint(f(1, 0));\nprint(\"depois\");",
			"antes\n", "2:23: divisão por zero"},
		{"tipos em tempo de execucao", "fn soma(a, b) { return a + b; }\nprint(soma(1, 2));\nprint(soma(1, \"x\"));",
			"3\n", "1:26: operador '+' não aplicável a int e texto"},
		{"indice fora dos limites", "let a = [1, 2, 3];\nlet i = 0;\nwhile (true) { print(a[i]); i = i + 1; }",
			"1\n2\n3\n", "3:23: índice 3 fora dos limites (tamanho 3)"},
		{"aridade em tempo de execucao", "fn f(a) { return a; }\nlet fs = [f];\nprint(fs[0](1));\nprint(fs[0](1, 2));",
			"1\n", "4:12: 'f' espera 1 argumento(s), recebeu 2"},
		{"estouro de pilha", "fn inf(n) { return inf(n + 1); }\ninf(0);", "", "1:23: estouro de pilha: recursão profunda demais"},
		{"condicao nao booleana", "fn f(x) { if (x) { return 1; } return 0; }\nprint(f(true));\nprint(f(3));",
			"1\n", "1:15: esperado bool, recebeu int"},
		{"chamar valor", "fn f(g) { return g(); }\nprint(f(fn() { return 7; }));\nprint(f(5));", "7\n", "1:19: valor do tipo int não é chamável"},
		{"erro de embutido", "let x = [1];\nprint(len(x));\nprint(len(5));", "1\n", "3:10: len não aplicável a int"},
		{"push em nao array", "fn g(v) { return push(v, 1); }\nprint(g([]));\nprint(g(\"s\"));", "[1]\n", "1:22: push requer array como primeiro argumento, recebeu texto"},
	}
	for _, c := range casos {
		t.Run(c.nome, func(t *testing.T) {
			for _, m := range modos {
				r := Executar(c.fonte, m.vm, m.otimi)
				if r.Falha == nil || r.Falha.Fase != erros.Execucao {
					t.Fatalf("[%s] esperado falha de execução, veio %+v", m.nome, r.Falha)
				}
				if r.Falha.Err.Error() != c.msg {
					t.Errorf("[%s] erro = %q, quer %q", m.nome, r.Falha.Err, c.msg)
				}
				if r.Saida != c.saida {
					t.Errorf("[%s] saída parcial = %q, quer %q", m.nome, r.Saida, c.saida)
				}
				if !strings.Contains(r.Falha.Diagnostico, "erro[execução]") || !strings.Contains(r.Falha.Diagnostico, " | ") {
					t.Errorf("[%s] diagnóstico sem trecho:\n%s", m.nome, r.Falha.Diagnostico)
				}
			}
		})
	}
}

func TestFalhaError(t *testing.T) {
	r := Executar("let = 1;", false, false)
	if r.Falha == nil || !strings.HasPrefix(r.Falha.Error(), "sintaxe: 1:5:") {
		t.Errorf("Error() = %v", r.Falha)
	}
}
