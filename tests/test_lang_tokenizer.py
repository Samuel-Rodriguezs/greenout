import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from lang_tokenizer import ErroLexico, Token, Tokenizador, tokenizador_aritmetico


class TestTokenizer(unittest.TestCase):
    def test_expressao(self):
        toks = tokenizador_aritmetico().lista("x = 3.5 + f(2)")
        self.assertEqual(
            [(t.tipo, t.valor) for t in toks],
            [("ID", "x"), ("OP", "="), ("NUMERO", "3.5"), ("OP", "+"), ("ID", "f"),
             ("LPAREN", "("), ("NUMERO", "2"), ("RPAREN", ")")],
        )

    def test_posicoes(self):
        toks = tokenizador_aritmetico().lista("a\n  b")
        self.assertEqual(toks[0], Token("ID", "a", 1, 1))
        self.assertEqual(toks[1], Token("ID", "b", 2, 3))

    def test_erro_com_posicao(self):
        with self.assertRaises(ErroLexico) as ctx:
            tokenizador_aritmetico().lista("1 + $")
        self.assertIn("coluna 5", str(ctx.exception))

    def test_ordem_das_regras(self):
        t = Tokenizador([("IGUAL", r"=="), ("ATRIB", r"="), ("ESPACO", r" +")])
        self.assertEqual([x.tipo for x in t.tokenizar("== =")], ["IGUAL", "ATRIB"])

    def test_vazio(self):
        self.assertEqual(tokenizador_aritmetico().lista(""), [])

    def test_sem_regras(self):
        with self.assertRaises(ValueError):
            Tokenizador([])

    def test_comentario_ignorado(self):
        t = Tokenizador([("COM", r"#[^\n]*"), ("PAL", r"\w+"), ("ESPACO", r"\s+")], ignorar=("ESPACO", "COM"))
        self.assertEqual([x.valor for x in t.tokenizar("a # nada\nb")], ["a", "b"])


if __name__ == "__main__":
    unittest.main()
