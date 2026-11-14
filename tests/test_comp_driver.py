import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from comp_driver import (BACKENDS, ErroCompilacao, blocos_da_principal, executar,
                         frontend, otimizar)
from comp_erros import formatar_erros
from comp_lexer import ErroLexico
from comp_parser import ErroSintaxe, parse
from comp_printer import formatar
from comp_vm import ErroExecucao

FATORIAL = """
// fatorial recursivo e iterativo
func fat(n: int) -> int {
    if (n <= 1) { return 1; }
    return n * fat(n - 1);
}
func fat_iter(n: int) -> int {
    var r = 1;
    var i = 2;
    while (i <= n) { r = r * i; i = i + 1; }
    return r;
}
print(fat(0));
print(fat(5));
print(fat(10));
print(fat_iter(10) == fat(10));
print(fat(20));
"""

FIBONACCI = """
func fib(n: int) -> int {
    if (n < 2) { return n; }
    return fib(n - 1) + fib(n - 2);
}
func fib_iter(n: int) -> int {
    var a = 0; var b = 1; var i = 0;
    while (i < n) { var t = a + b; a = b; b = t; i = i + 1; }
    return a;
}
var k = 0;
while (k < 10) { print(fib(k)); k = k + 1; }
print(fib_iter(50));
"""

PRIMOS = """
/* crivo por divisão: imprime os primos até 30 */
func primo(n: int) -> bool {
    if (n < 2) { return false; }
    var d = 2;
    while (d * d <= n) {
        if (n % d == 0) { return false; }
        d = d + 1;
    }
    return true;
}
var n = 2;
var total = 0;
while (n <= 30) {
    if (primo(n)) { print(n); total = total + 1; }
    n = n + 1;
}
print(total);
"""

MDC_COLLATZ = """
func mdc(a: int, b: int) -> int { while (b != 0) { var t = a % b; a = b; b = t; } return a; }
func passos(n: int) -> int {
    var c = 0;
    while (n != 1) { if (n % 2 == 0) { n = n / 2; } else { n = 3 * n + 1; } c = c + 1; }
    return c;
}
print(mdc(48, 18)); print(mdc(17, 5)); print(passos(27)); print(-17 / 5); print(-17 % 5);
"""

LOGICA = """
func ruido(v: bool) -> bool { print(777); return v; }
var a = 3; var b = 4;
print(a < b && b < 10);
print(!(a == b) || ruido(false));
print(a > b && ruido(true));
print(false || ruido(true));
{ var a = 100; print(a + b); }
print(a);
"""

PROGRAMAS = {
    "fatorial": (FATORIAL, ["1", "120", "3628800", "true", "2432902008176640000"]),
    "fibonacci": (FIBONACCI, ["0", "1", "1", "2", "3", "5", "8", "13", "21", "34", "12586269025"]),
    "primos": (PRIMOS, ["2", "3", "5", "7", "11", "13", "17", "19", "23", "29", "10"]),
    "mdc_collatz": (MDC_COLLATZ, ["6", "1", "111", "-3", "-2"]),
    "logica": (LOGICA, ["true", "true", "false", "777", "true", "104", "3"]),
}


class TestProgramasDePonta(unittest.TestCase):
    def test_todos_os_backends_e_otimizacoes(self):
        for nome, (fonte, esperado) in PROGRAMAS.items():
            for backend in BACKENDS:
                for otimizado in (False, True):
                    with self.subTest(programa=nome, backend=backend, otimizado=otimizado):
                        self.assertEqual(executar(fonte, backend, otimizado), esperado)

    def test_backend_desconhecido(self):
        with self.assertRaises(ValueError):
            executar("print(1);", "jit")

    def test_pretty_print_nao_muda_o_resultado(self):
        for nome, (fonte, esperado) in PROGRAMAS.items():
            with self.subTest(nome):
                reformatado = formatar(parse(fonte))
                self.assertEqual(executar(reformatado), esperado)


class TestOtimizador(unittest.TestCase):
    def test_programa_constante_vira_prints(self):
        fonte = """
        var a = 2 * 3; var b = a + 4; var c = b * 1;
        if (c > 5) { print(c); } else { print(0); }
        var inutil = 99;
        """
        otimizado = otimizar(frontend(fonte))
        self.assertEqual(otimizado, parse("print(10);"))

    def test_laco_com_acumulador_mantem_semantica(self):
        fonte = "var s = 0; var i = 0; while (i < 5) { s = s + i * 1; i = i + 1; } print(s);"
        otimizado = otimizar(frontend(fonte))
        self.assertEqual(executar(fonte, otimizado=True), ["10"])
        self.assertIn("while", formatar(otimizado))

    def test_otimizacao_reduz_blocos(self):
        programa = frontend("var f = false; if (f) { print(1); } else { print(2); } print(3);")
        self.assertLess(blocos_da_principal(otimizar(programa)), blocos_da_principal(programa))

    def test_funcao_nao_usada_removida(self):
        programa = frontend("func f() -> int { return 1; } print(2);")
        self.assertEqual(otimizar(programa).funcoes(), [])

    def test_idempotente(self):
        for fonte, _ in PROGRAMAS.values():
            uma = otimizar(frontend(fonte))
            self.assertEqual(otimizar(uma), uma)


class TestErrosDePonta(unittest.TestCase):
    def erros(self, fonte):
        with self.assertRaises(ErroCompilacao) as ctx:
            executar(fonte)
        return ctx.exception.erros

    def test_erro_lexico(self):
        (e,) = self.erros("var x = 1;\nvar y = 2 # 3;")
        self.assertIsInstance(e, ErroLexico)
        self.assertEqual((e.linha, e.coluna), (2, 11))

    def test_erro_sintatico(self):
        (e,) = self.erros("func f( { }")
        self.assertIsInstance(e, ErroSintaxe)

    def test_varios_erros_semanticos(self):
        fonte = "var a = 1;\nvar a = 2;\nprint(b);\nprint(f(1));"
        erros = self.erros(fonte)
        self.assertEqual(len(erros), 3)
        texto = formatar_erros(fonte, erros, "teste.mini")
        self.assertIn("teste.mini:2:5: erro semântico: 'a' já declarado neste escopo (linha 1)", texto)
        self.assertIn("variável 'b' não declarada", texto)
        self.assertIn("função 'f' não declarada", texto)
        self.assertTrue(texto.endswith("3 erros"))

    def test_erro_de_tipo(self):
        fonte = "var x = 1;\nif (x) { print(x + true); }"
        erros = self.erros(fonte)
        self.assertEqual(len(erros), 2)
        self.assertTrue(all(e.linha == 2 for e in erros))

    def test_tipos_nao_sao_checados_se_ha_erro_semantico(self):
        erros = self.erros("var x = y + true;")
        self.assertEqual([e.mensagem for e in erros], ["variável 'y' não declarada"])

    def test_erro_de_execucao_em_todos_os_backends(self):
        fonte = "func f(a: int) -> int { return 10 / a; } print(f(2)); print(f(0));"
        for backend in BACKENDS:
            with self.subTest(backend):
                with self.assertRaisesRegex(ErroExecucao, "divisão por zero"):
                    executar(fonte, backend)

    def test_saida_parcial_antes_do_erro_nao_vaza(self):
        with self.assertRaises(ErroExecucao):
            executar("print(1); print(1 / 0);")


if __name__ == "__main__":
    unittest.main()
