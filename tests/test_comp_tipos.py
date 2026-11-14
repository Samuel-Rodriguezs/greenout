import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from comp_parser import parse, parse_expressao
from comp_tipos import tipo_da_expressao, verificar


def erros(fonte):
    return [e.mensagem for e in verificar(parse(fonte))]


class TestTipos(unittest.TestCase):
    def test_programa_correto(self):
        fonte = """
        func par(n: int) -> bool { return n % 2 == 0; }
        func fat(n: int) -> int { if (n <= 1) { return 1; } else { return n * fat(n - 1); } }
        var x: int = fat(4); var b = par(x) && !(x > 100);
        while (b) { x = x - 1; b = x > 0; }
        print(b); print(x);
        """
        self.assertEqual(erros(fonte), [])

    def test_soma_com_bool(self):
        self.assertEqual(erros("var x = 1 + true;"),
                         ["operador '+' exige int, recebeu bool"])

    def test_condicao_nao_bool(self):
        self.assertEqual(erros("if (1) { } while (2 + 3) { }"),
                         ["condição do 'if' deve ser bool, não int",
                          "condição do 'while' deve ser bool, não int"])

    def test_anotacao_incompativel(self):
        self.assertEqual(erros("var x: bool = 3;"),
                         ["'x' declarado bool mas inicializado com int"])

    def test_atribuicao_de_tipo_diferente(self):
        self.assertEqual(erros("var x = 1; x = false;"),
                         ["atribuição de bool a 'x' do tipo int"])

    def test_igualdade_exige_mesmo_tipo(self):
        self.assertEqual(erros("var b = 1 == true;"), ["comparação '==' entre int e bool"])
        self.assertEqual(erros("var b = true != false; var c = 1 != 2;"), [])

    def test_logicos_e_negacao(self):
        self.assertEqual(erros("var b = 1 && true;"), ["operador '&&' exige bool, recebeu int"])
        self.assertEqual(erros("var b = !3;"), ["operador '!' exige bool, recebeu int"])
        self.assertEqual(erros("var b = -true;"), ["operador '-' exige int, recebeu bool"])

    def test_argumento_de_tipo_errado(self):
        msgs = erros("func f(a: int, b: bool) {} f(true, 1);")
        self.assertEqual(msgs, ["argumento 1 de 'f': esperado int, recebeu bool",
                                "argumento 2 de 'f': esperado bool, recebeu int"])

    def test_return_incompativel(self):
        self.assertEqual(erros("func f() -> int { return true; }"),
                         ["return de bool em função int"])
        self.assertEqual(erros("func f() { return 1; }"), ["return com valor em função void"])
        self.assertEqual(erros("func f() -> int { return; }"),
                         ["return sem valor em função int"])

    def test_falta_return(self):
        self.assertEqual(erros("func f(a: int) -> int { if (a > 0) { return 1; } }"),
                         ["função 'f' pode terminar sem retornar int"])
        self.assertEqual(erros("func f(a: int) -> int { while (true) { return 1; } }"),
                         ["função 'f' pode terminar sem retornar int"])

    def test_return_em_todos_os_ramos(self):
        self.assertEqual(
            erros("func f(a: int) -> int { if (a > 0) { return 1; } else { return 2; } }"), [])

    def test_void_nao_vira_valor(self):
        self.assertEqual(erros("func f() {} var x = f();"),
                         ["expressão sem valor (função void)"])
        self.assertEqual(erros("func f() {} f(); print(f());"),
                         ["expressão sem valor (função void)"])

    def test_inferencia_propaga(self):
        self.assertEqual(erros("var a = 1 < 2; var b = a + 1;"),
                         ["operador '+' exige int, recebeu bool"])

    def test_nao_declarado_nao_gera_erro_de_tipo(self):
        self.assertEqual(erros("var x = y + 1;"), [])

    def test_sombreamento_de_tipo(self):
        self.assertEqual(erros("var x = 1; { var x = true; print(x && true); } print(x + 1);"), [])

    def test_posicao_do_erro_no_operador(self):
        e = verificar(parse("var x =\n 1 + true;"))[0]
        self.assertEqual((e.linha, e.coluna), (2, 4))

    def test_tipo_da_expressao_avulsa(self):
        self.assertEqual(tipo_da_expressao(parse_expressao("a < 3"), variaveis={"a": "int"}),
                         "bool")
        self.assertEqual(tipo_da_expressao(parse_expressao("a + 3"), variaveis={"a": "int"}),
                         "int")


if __name__ == "__main__":
    unittest.main()
