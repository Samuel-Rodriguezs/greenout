import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from txt_tokenizador import tokenizar, tokenizar_sentencas


class TestTokenizador(unittest.TestCase):
    def test_acentos(self):
        self.assertEqual(tokenizar("Olá, São João!"), ["olá", "são", "joão"])

    def test_hifen_e_numeros(self):
        self.assertEqual(tokenizar("guarda-chuva 123 x2"), ["guarda-chuva", "x"])

    def test_manter_caixa(self):
        self.assertEqual(tokenizar("Ação", minusculas=False), ["Ação"])

    def test_vazio(self):
        self.assertEqual(tokenizar(""), [])
        self.assertEqual(tokenizar("!!! 123"), [])

    def test_sentencas(self):
        self.assertEqual(tokenizar_sentencas("Oi. Tudo bem? Sim!"), ["Oi.", "Tudo bem?", "Sim!"])
        self.assertEqual(tokenizar_sentencas("   "), [])


if __name__ == "__main__":
    unittest.main()
