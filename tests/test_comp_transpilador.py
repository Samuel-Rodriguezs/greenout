import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from comp_gerador import gerar
from comp_parser import parse
from comp_transpilador import executar_python, transpilar
from comp_vm import ErroExecucao, executar


def py(fonte):
    return executar_python(parse(fonte))


def vm(fonte):
    return executar(gerar(parse(fonte))).saida


PROGRAMAS = {
    "aritmetica": "print(2 + 3 * 4 - 1); print((7 - 2) * (3 + 1)); print(-7 / 2); print(-7 % 3); print(7 % -3);",
    "variaveis": "var a = 5; var b = a * 2; a = a + b; print(a); print(b);",
    "booleanos": "print(1 < 2 && 2 < 3); print(!(1 == 1) || false); print(true != false); print(!true);",
    "while": "var i = 0; var s = 0; while (i <= 10) { s = s + i * i; i = i + 1; } print(s);",
    "if_else": """
        func sinal(n: int) -> int {
            if (n < 0) { return -1; } else if (n == 0) { return 0; } else { return 1; }
        }
        print(sinal(-4)); print(sinal(0)); print(sinal(9));""",
    "recursao": "func fat(n: int) -> int { if (n <= 1) { return 1; } return n * fat(n - 1); } print(fat(15));",
    "sombreamento": "var x = 1; { var x = 2; x = x + 10; print(x); } print(x); if (true) { var x = 7; print(x); } print(x);",
    "curto_circuito": """
        func r(v: bool) -> bool { print(42); return v; }
        print(false && r(true)); print(true || r(true)); print(true && r(false)); print(false || r(true));""",
    "void": "func p(n: int) { if (n > 1) { print(n); return; } print(0); } p(1); p(5);",
    "mutua": """
        func par(n: int) -> bool { if (n == 0) { return true; } return impar(n - 1); }
        func impar(n: int) -> bool { if (n == 0) { return false; } return par(n - 1); }
        print(par(10)); print(impar(10));""",
    "blocos_vazios": "if (true) { } else { } while (false) { } func f() { } f(); print(1);",
}


class TestTranspilador(unittest.TestCase):
    def test_equivalente_a_vm(self):
        for nome, fonte in PROGRAMAS.items():
            with self.subTest(nome):
                self.assertEqual(py(fonte), vm(fonte))

    def test_codigo_gerado_tem_estrutura_esperada(self):
        codigo = transpilar(parse("func f(a: int) -> int { return a + 1; } var x = f(2); print(x);"))
        self.assertIn("def f_f(v_a):", codigo)
        self.assertIn("return (v_a + 1)", codigo)
        self.assertIn("def _principal():", codigo)
        self.assertIn("v_x = f_f(2)", codigo)
        compile(codigo, "<teste>", "exec")  # é Python válido

    def test_sem_preambulo(self):
        self.assertNotIn("def _div", transpilar(parse("print(1);"), com_preambulo=False))

    def test_nomes_que_sao_palavras_reservadas_do_python(self):
        fonte = "func lambda(class: int) -> int { return class; } print(lambda(3));"
        self.assertEqual(py(fonte), ["3"])
        fonte2 = "var None = 1; var pass = 2; print(None + pass);"
        self.assertEqual(py(fonte2), ["3"])

    def test_variavel_e_funcao_com_mesmo_nome(self):
        self.assertEqual(py("func v() -> int { return 4; } var v = 10; print(v + 1);"), ["11"])

    def test_numero_negativo_literal(self):
        from comp_ast import Binario, Num, Programa, Imprimir
        p = Programa([Imprimir(Binario("-", Num(1), Num(-2)))])
        self.assertEqual(executar_python(p), ["3"])

    def test_divisao_por_zero_vira_erro_de_execucao(self):
        with self.assertRaisesRegex(ErroExecucao, "divisão por zero"):
            py("var z = 0; print(5 / z);")

    def test_recursao_infinita(self):
        with self.assertRaisesRegex(ErroExecucao, "pilha"):
            py("func f(n: int) -> int { return f(n + 1); } print(f(0));")

    def test_recursao_profunda_ok(self):
        self.assertEqual(py("func s(n: int) -> int { if (n == 0) { return 0; } return n + s(n - 1); } print(s(1500));"),
                         ["1125750"])

    def test_limite_de_recursao_restaurado(self):
        antes = sys.getrecursionlimit()
        py("print(1);")
        self.assertEqual(sys.getrecursionlimit(), antes)


if __name__ == "__main__":
    unittest.main()
