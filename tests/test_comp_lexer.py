import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from comp_lexer import ErroLexico, ErroMini, TipoToken, tokenizar


def lexemas(fonte):
    return [t.lexema for t in tokenizar(fonte)[:-1]]


class TestLexer(unittest.TestCase):
    def test_tokens_basicos_e_posicoes(self):
        toks = tokenizar("var x = 10;\nx = x+1;")
        self.assertEqual([t.lexema for t in toks[:-1]],
                         ["var", "x", "=", "10", ";", "x", "=", "x", "+", "1", ";"])
        self.assertEqual((toks[0].linha, toks[0].coluna), (1, 1))
        self.assertEqual((toks[1].linha, toks[1].coluna), (1, 5))
        self.assertEqual((toks[5].linha, toks[5].coluna), (2, 1))
        self.assertEqual(toks[-1].tipo, TipoToken.EOF)

    def test_tipos(self):
        toks = tokenizar("while foo 42 <=")
        self.assertEqual([t.tipo for t in toks[:-1]],
                         [TipoToken.KEYWORD, TipoToken.ID, TipoToken.NUM, TipoToken.OP])

    def test_operadores_de_dois_caracteres(self):
        self.assertEqual(lexemas("a==b!=c<=d>=e&&f||g->h"),
                         ["a", "==", "b", "!=", "c", "<=", "d", ">=", "e", "&&",
                          "f", "||", "g", "->", "h"])

    def test_comentarios(self):
        self.assertEqual(lexemas("a // resto\nb /* x\ny */ c"), ["a", "b", "c"])
        toks = tokenizar("/* x\ny */ c")
        self.assertEqual((toks[0].linha, toks[0].coluna), (2, 6))

    def test_comentario_nao_terminado(self):
        with self.assertRaises(ErroLexico) as ctx:
            tokenizar("a\n  /* abc")
        self.assertEqual((ctx.exception.linha, ctx.exception.coluna), (2, 3))

    def test_caractere_invalido(self):
        with self.assertRaises(ErroLexico) as ctx:
            tokenizar("var x = 3 @ 4;")
        self.assertEqual(ctx.exception.coluna, 11)
        self.assertIsInstance(ctx.exception, ErroMini)

    def test_operador_incompleto(self):
        with self.assertRaises(ErroLexico):
            tokenizar("a & b")
        with self.assertRaises(ErroLexico):
            tokenizar("a | b")

    def test_numero_malformado(self):
        with self.assertRaises(ErroLexico) as ctx:
            tokenizar("x = 12abc;")
        self.assertEqual(ctx.exception.tamanho, 5)

    def test_identificador_com_underscore_e_digitos(self):
        self.assertEqual(lexemas("_a1 b_2"), ["_a1", "b_2"])


if __name__ == "__main__":
    unittest.main()
