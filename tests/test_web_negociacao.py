import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from web_negociacao import escolher, escolher_idioma, parse_accept


class TestWebNegociacao(unittest.TestCase):
    def test_parse_ordena(self):
        itens = parse_accept("text/*;q=0.5, */*;q=0.1, application/json, text/html;q=0.5")
        self.assertEqual([i.valor for i in itens],
                         ["application/json", "text/html", "text/*", "*/*"])

    def test_parse_vazio(self):
        self.assertEqual(parse_accept(None)[0].valor, "*/*")
        self.assertEqual(parse_accept("  ")[0].valor, "*/*")

    def test_parse_q_invalido(self):
        with self.assertRaises(ValueError):
            parse_accept("text/html;q=abc")
        with self.assertRaises(ValueError):
            parse_accept("text/html;q=2")

    def test_escolher_preferido(self):
        self.assertEqual(escolher("application/json, text/html;q=0.5",
                                  ["text/html", "application/json"]), "application/json")

    def test_curinga(self):
        self.assertEqual(escolher("text/*", ["application/json", "text/csv"]), "text/csv")
        self.assertEqual(escolher("*/*", ["a/b", "c/d"]), "a/b")
        self.assertEqual(escolher(None, ["a/b"]), "a/b")

    def test_nenhum_aceitavel(self):
        self.assertIsNone(escolher("image/png", ["text/html"]))

    def test_q_zero_exclui(self):
        self.assertEqual(escolher("*/*, text/html;q=0", ["text/html", "text/plain"]), "text/plain")
        self.assertIsNone(escolher("text/html;q=0", ["text/html"]))

    def test_especificidade_define_q(self):
        # text/html tem q=1 (regra exata), mesmo com text/* a 0.1
        self.assertEqual(escolher("text/*;q=0.1, text/html", ["text/plain", "text/html"]),
                         "text/html")

    def test_empate_usa_ordem_do_servidor(self):
        self.assertEqual(escolher("a/b, c/d", ["c/d", "a/b"]), "c/d")

    def test_idioma(self):
        disp = ["en", "pt-BR"]
        self.assertEqual(escolher_idioma("pt;q=0.9, en;q=0.8", disp), "pt-BR")
        self.assertEqual(escolher_idioma("fr, en;q=0.5", disp), "en")
        self.assertEqual(escolher_idioma("fr", disp, "en"), "en")
        self.assertEqual(escolher_idioma(None, disp, "en"), "en")
        self.assertEqual(escolher_idioma("pt-br", disp), "pt-BR")


if __name__ == "__main__":
    unittest.main()
