import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

import sig_convolucao as c


class TestConvolucao(unittest.TestCase):
    def test_basica(self):
        self.assertEqual(c.convolucao([1, 2, 3], [0, 1, 0.5]), [0, 1, 2.5, 4, 1.5])

    def test_identidade(self):
        self.assertEqual(c.convolucao([4, 5, 6], [1]), [4, 5, 6])

    def test_comutativa(self):
        a, b = [1, -2, 3], [4, 0, 1, 2]
        self.assertEqual(c.convolucao(a, b), c.convolucao(b, a))

    def test_vazia(self):
        self.assertEqual(c.convolucao([], [1]), [])

    def test_mesma(self):
        self.assertEqual(c.convolucao_mesma([1, 2, 3], [1, 1, 1]), [3, 6, 5])

    def test_autocorrelacao(self):
        self.assertEqual(c.autocorrelacao([1, 2, 3]), [14, 8, 3])

    def test_correlacao_cruzada(self):
        self.assertEqual(c.correlacao_cruzada([1, 2], [1, 2]), [2, 5, 2])

    def test_lag(self):
        y = [1, 3, 2]
        x = [0, 0, 0, 1, 3, 2, 0]
        self.assertEqual(c.lag_do_maximo(x, y), 3)
        with self.assertRaises(ValueError):
            c.lag_do_maximo([], [1])


if __name__ == "__main__":
    unittest.main()
