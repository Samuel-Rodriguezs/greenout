import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from dp_chain_of_responsibility import Aprovador, cadeia_padrao


class TestChain(unittest.TestCase):
    def test_niveis(self):
        c = cadeia_padrao()
        self.assertEqual(c.aprovar(500), "gerente")
        self.assertEqual(c.aprovar(1000), "gerente")
        self.assertEqual(c.aprovar(5000), "diretor")
        self.assertEqual(c.aprovar(50000), "presidente")

    def test_acima_de_tudo(self):
        with self.assertRaises(ValueError):
            cadeia_padrao().aprovar(1_000_000)

    def test_elo_unico(self):
        with self.assertRaises(ValueError):
            Aprovador("x", 1).aprovar(2)


if __name__ == "__main__":
    unittest.main()
