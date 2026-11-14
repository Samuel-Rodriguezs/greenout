import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from comp_parser import parse
from comp_semantica import analisar
from comp_simbolos import ErroRedeclaracao


def mensagens(fonte):
    return [e.mensagem for e in analisar(parse(fonte)).erros]


class TestSemantica(unittest.TestCase):
    def test_programa_valido(self):
        fonte = """
        func fat(n: int) -> int { if (n <= 1) { return 1; } return n * fat(n - 1); }
        var r = fat(5); print(r);
        """
        res = analisar(parse(fonte))
        self.assertTrue(res.ok)

    def test_variavel_nao_declarada(self):
        erros = analisar(parse("var a = 1;\nprint(b);")).erros
        self.assertEqual(len(erros), 1)
        self.assertIn("'b' não declarada", erros[0].mensagem)
        self.assertEqual((erros[0].linha, erros[0].coluna), (2, 7))

    def test_atribuicao_a_nao_declarada(self):
        self.assertEqual(mensagens("x = 1;"), ["variável 'x' não declarada"])

    def test_redeclaracao_mesmo_escopo(self):
        erros = analisar(parse("var x = 1;\nvar x = 2;")).erros
        self.assertEqual(len(erros), 1)
        self.assertIsInstance(erros[0], ErroRedeclaracao)
        self.assertEqual(erros[0].linha, 2)

    def test_sombreamento_permitido(self):
        self.assertEqual(mensagens("var x = 1; { var x = 2; print(x); } print(x);"), [])

    def test_uso_na_propria_inicializacao(self):
        self.assertEqual(mensagens("var x = x + 1;"), ["variável 'x' não declarada"])

    def test_variavel_de_bloco_nao_vaza(self):
        self.assertEqual(len(mensagens("if (true) { var t = 1; } print(t);")), 1)

    def test_param_redeclarado_no_corpo(self):
        self.assertEqual(len(mensagens("func f(a: int) { var a = 2; }")), 1)

    def test_param_duplicado(self):
        self.assertEqual(len(mensagens("func f(a: int, a: int) {}")), 1)

    def test_funcao_duplicada(self):
        self.assertEqual(len(mensagens("func f() {} func f() {}")), 1)

    def test_aridade(self):
        msgs = mensagens("func f(a: int, b: int) -> int { return a; } print(f(1));")
        self.assertEqual(msgs, ["função 'f' espera 2 argumento(s), recebeu 1"])

    def test_funcao_nao_declarada(self):
        self.assertEqual(mensagens("g(1);"), ["função 'g' não declarada"])

    def test_chamada_antes_da_declaracao(self):
        self.assertEqual(mensagens("print(f()); func f() -> int { return 1; }"), [])

    def test_variavel_chamada_como_funcao(self):
        self.assertEqual(mensagens("var x = 1; x(2);"), ["'x' não é uma função"])

    def test_funcao_usada_como_variavel(self):
        self.assertEqual(mensagens("func f() {} var y = f;"),
                         ["'f' é uma função, não uma variável"])

    def test_funcao_nao_ve_variaveis_do_main(self):
        msgs = mensagens("var g = 1; func f() -> int { return g; }")
        self.assertEqual(msgs, ["variável 'g' não declarada"])

    def test_return_fora_de_funcao(self):
        self.assertEqual(mensagens("return 1;"), ["'return' fora de função"])

    def test_acumula_varios_erros(self):
        self.assertEqual(len(mensagens("a = 1; b = 2; print(c);")), 3)

    def test_tabela_contem_escopos(self):
        res = analisar(parse("func f(a: int) { var b = a; } var z = 1;"))
        caminhos = {(c, s.nome) for c, s in res.tabela.todos()}
        self.assertIn(("global/f", "a"), caminhos)
        self.assertIn(("global/f", "b"), caminhos)
        self.assertIn(("global/main", "z"), caminhos)


if __name__ == "__main__":
    unittest.main()
