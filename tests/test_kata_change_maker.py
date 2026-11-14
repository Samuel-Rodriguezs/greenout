import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from kata_change_maker import fazer_troco


class TestKataChangeMaker(unittest.TestCase):
    def test_zero(self):
        self.assertEqual(fazer_troco(0), {})

    def test_uma_peca(self):
        self.assertEqual(fazer_troco(25), {25: 1})
        self.assertEqual(fazer_troco(10000), {10000: 1})

    def test_combinacao_brl(self):
        self.assertEqual(fazer_troco(1785), {1000: 1, 500: 1, 200: 1, 50: 1, 25: 1, 10: 1})

    def test_repeticao(self):
        self.assertEqual(fazer_troco(30000), {10000: 3})

    def test_soma_confere(self):
        for v in range(0, 3000, 55):
            troco = fazer_troco(v)
            self.assertEqual(sum(d * q for d, q in troco.items()), v)

    def test_sistema_nao_canonico(self):
        self.assertEqual(fazer_troco(6, (1, 3, 4)), {3: 2})
        self.assertEqual(fazer_troco(63, (1, 5, 10, 21, 25)), {21: 3})

    def test_impossivel(self):
        with self.assertRaises(ValueError):
            fazer_troco(7)  # menor denominação BRL é 5
        with self.assertRaises(ValueError):
            fazer_troco(3, (2,))

    def test_invalidos(self):
        with self.assertRaises(ValueError):
            fazer_troco(-1)
        with self.assertRaises(ValueError):
            fazer_troco(5, (0, 5))
        with self.assertRaises(ValueError):
            fazer_troco(5, ())


if __name__ == "__main__":
    unittest.main()
