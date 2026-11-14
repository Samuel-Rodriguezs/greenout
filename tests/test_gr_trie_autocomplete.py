import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from gr_trie_autocomplete import Autocompletar


class TestAutocompletar(unittest.TestCase):
    def setUp(self):
        self.a = Autocompletar()
        for p, w in [("casa", 5), ("caso", 2), ("casaco", 2), ("carro", 9), ("cama", 2), ("bola", 1)]:
            self.a.adicionar(p, w)

    def test_ordem_por_frequencia_e_alfabetica(self):
        self.assertEqual(self.a.sugerir("ca"), ["carro", "casa", "cama", "casaco", "caso"])

    def test_limite(self):
        self.assertEqual(self.a.sugerir("ca", 2), ["carro", "casa"])
        self.assertEqual(self.a.sugerir("ca", 0), [])

    def test_prefixo_inexistente(self):
        self.assertEqual(self.a.sugerir("zz"), [])

    def test_prefixo_vazio_lista_tudo(self):
        self.assertEqual(len(self.a.sugerir("", 100)), 6)

    def test_palavra_exata_inclusa(self):
        self.assertIn("casa", self.a.sugerir("casa"))

    def test_acumula_peso_e_contagem(self):
        self.a.adicionar("bola", 10)
        self.assertEqual(len(self.a), 6)
        self.assertEqual(self.a.sugerir("b"), ["bola"])
        self.assertTrue(self.a.contem("bola"))
        self.assertFalse(self.a.contem("bol"))

    def test_entradas_invalidas(self):
        with self.assertRaises(ValueError):
            self.a.adicionar("")
        with self.assertRaises(ValueError):
            self.a.adicionar("x", 0)


if __name__ == "__main__":
    unittest.main()
