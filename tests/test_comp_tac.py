import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from comp_gerador import gerar
from comp_parser import parse
from comp_tac import (Bin, Chama, Copia, Imprime, Param, Retorna, Rotulo, Salto,
                      SaltoSeNao, Un, definido, executar_tac, formatar_tac,
                      gerar_tac, usados)
from comp_vm import ErroExecucao, executar


def tac(fonte):
    return gerar_tac(parse(fonte))


def roda_tac(fonte):
    return executar_tac(tac(fonte))


class TestTac(unittest.TestCase):
    def test_expressao_tres_enderecos(self):
        p = tac("var a = 1; var b = 2; var c = a + b * 3;")
        self.assertEqual(p.principal.codigo, [
            Copia("a", 1), Copia("b", 2),
            Bin("%t1", "*", "b", 3), Bin("%t2", "+", "a", "%t1"), Copia("c", "%t2"),
            Retorna(None)])

    def test_texto(self):
        p = tac("var x = 2; if (x < 3) { print(x); } else { print(0); }")
        self.assertEqual(formatar_tac(p).splitlines(), [
            "func main():",
            "    x = 2",
            "    %t1 = x < 3",
            "    ifFalse %t1 goto L2",
            "    print x",
            "    goto L1",
            "L2:",
            "    print 0",
            "L1:",
            "    return"])

    def test_while(self):
        p = tac("var i = 0; while (i < 2) { i = i + 1; }")
        ins = p.principal.codigo
        self.assertIsInstance(ins[1], Rotulo)
        self.assertIsInstance(ins[3], SaltoSeNao)
        self.assertEqual(ins[-3], Salto(ins[1].nome))

    def test_chamada_com_params(self):
        p = tac("func f(a: int, b: int) -> int { return a - b; } print(f(1 + 1, 5));")
        ins = p.principal.codigo
        self.assertEqual(ins[:5], [Bin("%t1", "+", 1, 1), Param("%t1"), Param(5),
                                   Chama("%t2", "f", 2), Imprime("%t2")])
        self.assertEqual(p.funcoes[0].params, ["a", "b"])
        self.assertEqual(p.funcoes[0].codigo[-1], Retorna(0))

    def test_args_aninhados_nao_se_misturam(self):
        fonte = """
        func g(a: int) -> int { return a * 2; }
        func f(a: int, b: int) -> int { return a - b; }
        print(f(g(5), g(1)));
        """
        self.assertEqual(roda_tac(fonte), ["8"])

    def test_variaveis_sombreadas_ganham_sufixo(self):
        p = tac("var x = 1; { var x = 2; print(x); } print(x);")
        self.assertEqual(p.principal.codigo[:4],
                         [Copia("x", 1), Copia("x.1", 2), Imprime("x.1"), Imprime("x")])

    def test_curto_circuito_vira_salto(self):
        p = tac("var a = true; var b = false; var c = a && b;")
        self.assertTrue(any(isinstance(i, SaltoSeNao) for i in p.principal.codigo))
        p2 = tac("var a = true; var c = a || false;")
        self.assertTrue(any(isinstance(i, Un) and i.op == "!" for i in p2.principal.codigo))

    def test_usados_e_definido(self):
        i = Bin("%t1", "+", "a", 3)
        self.assertEqual(usados(i), ["a"])
        self.assertEqual(definido(i), "%t1")
        self.assertEqual(usados(Retorna("x")), ["x"])
        self.assertEqual(usados(Retorna(None)), [])
        self.assertEqual(usados(Param(True)), [])
        self.assertIsNone(definido(Imprime("x")))
        self.assertEqual(usados(SaltoSeNao("c", "L1")), ["c"])

    def test_interprete_programas(self):
        fonte = """
        func fib(n: int) -> int { if (n < 2) { return n; } return fib(n - 1) + fib(n - 2); }
        var i = 0;
        while (i < 10) { print(fib(i)); i = i + 1; }
        print(true && !(3 > 4)); print(false || 1 == 2); print(-7 / 2); print(-7 % 3);
        """
        self.assertEqual(roda_tac(fonte), executar(gerar(parse(fonte))).saida)

    def test_equivalencia_com_vm_curto_circuito(self):
        fonte = """
        func r(v: bool) -> bool { print(42); return v; }
        print(false && r(true)); print(true || r(true)); print(true && r(false)); print(false || r(true));
        """
        self.assertEqual(roda_tac(fonte), executar(gerar(parse(fonte))).saida)

    def test_erros_de_execucao(self):
        with self.assertRaises(ErroExecucao):
            roda_tac("var z = 0; print(1 % z);")
        with self.assertRaises(ErroExecucao):
            roda_tac("func f(n: int) -> int { return f(n + 1); } print(f(0));")

    def test_funcao_void_sem_retorno(self):
        self.assertEqual(roda_tac("func p(n: int) { print(n); } p(3); p(4);"), ["3", "4"])


if __name__ == "__main__":
    unittest.main()
