import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from crip_bloom import FiltroBloom


class TestBloom(unittest.TestCase):
    def test_sem_falso_negativo(self):
        f = FiltroBloom.para(500, 0.01)
        itens = [f"item{i}" for i in range(500)]
        for i in itens:
            f.adicionar(i)
        self.assertTrue(all(i in f for i in itens))

    def test_falsos_positivos_controlados(self):
        f = FiltroBloom.para(1000, 0.01)
        for i in range(1000):
            f.adicionar(f"in{i}")
        fp = sum(f"out{i}" in f for i in range(5000)) / 5000
        self.assertLess(fp, 0.03)
        self.assertAlmostEqual(f.taxa_estimada(), 0.01, delta=0.005)

    def test_vazio(self):
        self.assertNotIn("x", FiltroBloom(64, 3))

    def test_bytes_e_str_equivalentes(self):
        f = FiltroBloom(256, 3)
        f.adicionar("olá")
        self.assertIn("olá".encode(), f)

    def test_dimensionamento(self):
        f = FiltroBloom.para(1000, 0.01)
        self.assertEqual((f.bits, f.hashes), (9586, 7))

    def test_erros(self):
        for args in ((0, 1), (1, 0)):
            with self.assertRaises(ValueError):
                FiltroBloom(*args)
        with self.assertRaises(ValueError):
            FiltroBloom.para(10, 1.5)


if __name__ == "__main__":
    unittest.main()
