import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from comp_ast import (Atrib, Binario, Bloco, Bool, Chamada, Enquanto, ExprStmt,
                      Funcao, Imprimir, Nome, Num, Param, Retorno, Se, Unario, Var)
from comp_lexer import ErroLexico
from comp_parser import ErroSintaxe, parse, parse_expressao


class TestParserExpressoes(unittest.TestCase):
    def test_precedencia_mult_sobre_soma(self):
        self.assertEqual(parse_expressao("1 + 2 * 3"),
                         Binario("+", Num(1), Binario("*", Num(2), Num(3))))

    def test_associatividade_esquerda(self):
        self.assertEqual(parse_expressao("10 - 3 - 2"),
                         Binario("-", Binario("-", Num(10), Num(3)), Num(2)))

    def test_parenteses(self):
        self.assertEqual(parse_expressao("(1 + 2) * 3"),
                         Binario("*", Binario("+", Num(1), Num(2)), Num(3)))

    def test_logicos_e_comparacao(self):
        e = parse_expressao("a < b && c == d || !e")
        esperado = Binario("||",
                           Binario("&&", Binario("<", Nome("a"), Nome("b")),
                                   Binario("==", Nome("c"), Nome("d"))),
                           Unario("!", Nome("e")))
        self.assertEqual(e, esperado)

    def test_unario_liga_mais_forte(self):
        self.assertEqual(parse_expressao("-a * b"),
                         Binario("*", Unario("-", Nome("a")), Nome("b")))
        self.assertEqual(parse_expressao("- - 3"), Unario("-", Unario("-", Num(3))))

    def test_chamada(self):
        self.assertEqual(parse_expressao("f(1, g(x), 2+3)"),
                         Chamada("f", [Num(1), Chamada("g", [Nome("x")]),
                                       Binario("+", Num(2), Num(3))]))
        self.assertEqual(parse_expressao("f()"), Chamada("f", []))

    def test_literais_booleanos(self):
        self.assertEqual(parse_expressao("true && false"),
                         Binario("&&", Bool(True), Bool(False)))

    def test_posicao_dos_nos(self):
        e = parse_expressao("a +\n  b")
        self.assertEqual(e.pos, (1, 3))
        self.assertEqual(e.dir.pos, (2, 3))


class TestParserComandos(unittest.TestCase):
    def test_var_com_e_sem_tipo(self):
        p = parse("var x = 1; var y: bool = true;")
        self.assertEqual(p.itens, [Var("x", Num(1)), Var("y", Bool(True), "bool")])

    def test_atribuicao_e_expr_stmt(self):
        p = parse("x = 2; f(x);")
        self.assertEqual(p.itens, [Atrib("x", Num(2)),
                                   ExprStmt(Chamada("f", [Nome("x")]))])

    def test_if_else_if_else(self):
        p = parse("if (a) { x = 1; } else if (b) { x = 2; } else { x = 3; }")
        se = p.itens[0]
        self.assertIsInstance(se, Se)
        interno = se.senao.stmts[0]
        self.assertIsInstance(interno, Se)
        self.assertEqual(interno.senao, Bloco([Atrib("x", Num(3))]))

    def test_while_return_print(self):
        p = parse("while (i < 3) { print(i); i = i + 1; } ")
        w = p.itens[0]
        self.assertIsInstance(w, Enquanto)
        self.assertIsInstance(w.corpo.stmts[0], Imprimir)

    def test_funcao(self):
        p = parse("func soma(a: int, b: int) -> int { return a + b; }")
        f = p.itens[0]
        self.assertEqual(f, Funcao("soma", [Param("a", "int"), Param("b", "int")],
                                   "int", Bloco([Retorno(Binario("+", Nome("a"), Nome("b")))])))

    def test_funcao_void_por_padrao(self):
        f = parse("func f() { return; }").itens[0]
        self.assertEqual(f.ret, "void")
        self.assertEqual(f.corpo.stmts, [Retorno(None)])

    def test_bloco_solto_e_comentarios(self):
        p = parse("// c\n{ var a = 1; } /* fim */")
        self.assertIsInstance(p.itens[0], Bloco)

    def test_programa_vazio(self):
        self.assertEqual(parse("  // nada\n").itens, [])


class TestParserErros(unittest.TestCase):
    def assertErro(self, fonte, trecho, linha=None, coluna=None):
        with self.assertRaises(ErroSintaxe) as ctx:
            parse(fonte)
        self.assertIn(trecho, ctx.exception.mensagem)
        if linha is not None:
            self.assertEqual((ctx.exception.linha, ctx.exception.coluna), (linha, coluna))

    def test_ponto_e_virgula_faltando(self):
        self.assertErro("var x = 1\nvar y = 2;", "esperado ';'", 2, 1)

    def test_fim_inesperado(self):
        self.assertErro("while (true) {", "fim do arquivo")

    def test_expressao_faltando(self):
        self.assertErro("var x = ;", "esperado expressão", 1, 9)

    def test_parentese_nao_fechado(self):
        self.assertErro("print((1 + 2);", "esperado ')'")

    def test_funcao_aninhada(self):
        self.assertErro("{ func f() {} }", "nível superior", 1, 3)

    def test_param_sem_tipo(self):
        self.assertErro("func f(a) {}", "esperado ':'")

    def test_param_void_invalido(self):
        self.assertErro("func f(a: void) {}", "esperado tipo")

    def test_expressao_depois_de_expressao(self):
        with self.assertRaises(ErroSintaxe):
            parse_expressao("1 2")

    def test_erro_lexico_propaga(self):
        with self.assertRaises(ErroLexico):
            parse("var x = #;")


if __name__ == "__main__":
    unittest.main()
