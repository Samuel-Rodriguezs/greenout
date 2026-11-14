import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from mat_bissecao import bissecao


class TestBissecao(unittest.TestCase):
    def test_raiz_de_2(self):
        self.assertAlmostEqual(bissecao(lambda x: x * x - 2, 0, 2), 2 ** 0.5, places=9)

    def test_extremidade_raiz(self):
        self.assertEqual(bissecao(lambda x: x - 1, 1, 5), 1)
        self.assertEqual(bissecao(lambda x: x - 5, 1, 5), 5)

    def test_sem_mudanca_de_sinal(self):
        with self.assertRaises(ValueError):
            bissecao(lambda x: x * x + 1, -1, 1)

    def test_funcao_decrescente(self):
        self.assertAlmostEqual(bissecao(lambda x: 3 - x, 0, 10), 3.0, places=9)

    def test_raiz_exata_no_meio(self):
        self.assertEqual(bissecao(lambda x: x, -1, 1), 0.0)


if __name__ == "__main__":
    unittest.main()
