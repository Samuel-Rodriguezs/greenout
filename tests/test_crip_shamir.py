import itertools
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from crip_shamir import dividir, dividir_bytes, reconstruir, reconstruir_bytes


class TestShamir(unittest.TestCase):
    def test_qualquer_subconjunto_de_k(self):
        partes = dividir(123456789, 5, 3)
        for sub in itertools.combinations(partes, 3):
            self.assertEqual(reconstruir(list(sub)), 123456789)
        self.assertEqual(reconstruir(partes), 123456789)  # mais que k também funciona

    def test_menos_que_k_nao_revela(self):
        partes = dividir(42, 5, 3)
        self.assertNotEqual(reconstruir(partes[:2]), 42)

    def test_k_igual_1_e_n(self):
        self.assertEqual({y for _, y in dividir(7, 4, 1)}, {7})
        self.assertEqual(reconstruir(dividir(99, 4, 4)), 99)

    def test_corpo_pequeno_conhecido(self):
        # f(x) = 1234 + 166x + 94x^2 (exemplo da Wikipédia), p = 1613
        p = 1613
        partes = [(x, (1234 + 166 * x + 94 * x * x) % p) for x in (2, 4, 5)]
        self.assertEqual(reconstruir(partes, p), 1234)

    def test_bytes(self):
        for s in (b"", b"\x00\x00senha", "açúcar secreto".encode(), b"x" * 65):
            self.assertEqual(reconstruir_bytes(dividir_bytes(s, 5, 2)[2:4]), s)

    def test_erros(self):
        with self.assertRaises(ValueError):
            dividir(1, 3, 4)
        with self.assertRaises(ValueError):
            dividir(-1, 3, 2)
        with self.assertRaises(ValueError):
            reconstruir([(1, 5), (1, 6)])
        with self.assertRaises(ValueError):
            dividir_bytes(b"x" * 66, 3, 2)


if __name__ == "__main__":
    unittest.main()
