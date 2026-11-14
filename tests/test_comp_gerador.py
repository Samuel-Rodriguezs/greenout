import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from comp_gerador import gerar
from comp_parser import parse
from comp_vm import ErroExecucao, Op, executar


def roda(fonte, **kw):
    return executar(gerar(parse(fonte)), **kw).saida


class TestGerador(unittest.TestCase):
    def test_aritmetica_com_precedencia(self):
        self.assertEqual(roda("print(2 + 3 * 4); print((2 + 3) * 4); print(10 - 4 - 3);"),
                         ["14", "20", "3"])

    def test_divisao_e_resto_negativos(self):
        self.assertEqual(roda("print(-7 / 2); print(-7 % 2); print(7 / -2);"),
                         ["-3", "-1", "-3"])

    def test_variaveis_e_atribuicao(self):
        self.assertEqual(roda("var a = 5; var b = a * 2; a = a + b; print(a); print(b);"),
                         ["15", "10"])

    def test_if_else(self):
        fonte = """
        func sinal(n: int) -> int {
            if (n < 0) { return -1; } else if (n == 0) { return 0; } else { return 1; }
        }
        print(sinal(-9)); print(sinal(0)); print(sinal(42));
        """
        self.assertEqual(roda(fonte), ["-1", "0", "1"])

    def test_while(self):
        self.assertEqual(roda("var i = 0; var s = 0; while (i <= 4) { s = s + i; i = i + 1; } print(s);"),
                         ["10"])

    def test_recursao(self):
        fonte = "func fat(n: int) -> int { if (n <= 1) { return 1; } return n * fat(n - 1); } print(fat(10));"
        self.assertEqual(roda(fonte), ["3628800"])

    def test_booleanos(self):
        self.assertEqual(roda("print(1 < 2 && 2 < 3); print(!(1 == 1) || false); print(true != false);"),
                         ["true", "false", "true"])

    def test_curto_circuito_nao_avalia_lado_direito(self):
        fonte = """
        func ruido(v: bool) -> bool { print(99); return v; }
        print(false && ruido(true));
        print(true || ruido(false));
        print(true && ruido(false));
        print(false || ruido(true));
        """
        self.assertEqual(roda(fonte),
                         ["false", "true", "99", "false", "99", "true"])

    def test_sombreamento_de_escopo(self):
        fonte = "var x = 1; { var x = 2; x = x + 10; print(x); } print(x);"
        self.assertEqual(roda(fonte), ["12", "1"])

    def test_funcao_void_e_expr_stmt(self):
        fonte = "func ola(n: int) { print(n); return; print(0); } ola(7); ola(8);"
        self.assertEqual(roda(fonte), ["7", "8"])

    def test_parametros_nao_vazam_entre_chamadas(self):
        fonte = """
        func f(a: int, b: int) -> int { var t = a - b; return t; }
        print(f(10, 3)); print(f(3, 10));
        """
        self.assertEqual(roda(fonte), ["7", "-7"])

    def test_chamada_antes_da_declaracao_e_mutua(self):
        fonte = """
        func par(n: int) -> bool { if (n == 0) { return true; } return impar(n - 1); }
        func impar(n: int) -> bool { if (n == 0) { return false; } return par(n - 1); }
        print(par(10)); print(impar(7)); print(par(3));
        """
        self.assertEqual(roda(fonte), ["true", "true", "false"])

    def test_nomes_do_escopo_principal(self):
        prog = gerar(parse("var a = 1; var b = 2; { var c = 3; }"))
        self.assertEqual(prog.nomes_principal, {"a": 0, "b": 1})
        self.assertEqual(prog.principal.n_locais, 3)

    def test_saltos_dentro_dos_limites(self):
        prog = gerar(parse("var i = 0; while (i < 3) { if (i == 1) { print(i); } i = i + 1; }"))
        n = len(prog.principal.codigo)
        for ins in prog.principal.codigo:
            if ins.op in (Op.JMP, Op.JZ):
                self.assertTrue(0 <= ins.arg < n)
        self.assertEqual(prog.principal.codigo[-1].op, Op.HALT)

    def test_erro_de_execucao_propagado(self):
        with self.assertRaises(ErroExecucao):
            roda("var z = 0; print(1 / z);")


if __name__ == "__main__":
    unittest.main()
