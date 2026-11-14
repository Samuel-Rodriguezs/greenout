import random
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from sim_forca import Forca


class TestForca(unittest.TestCase):
    def test_vitoria(self):
        f = Forca("gato")
        for c in "gato":
            self.assertTrue(f.chutar(c))
        self.assertTrue(f.venceu)
        self.assertEqual(f.mascara, "g a t o")

    def test_derrota(self):
        f = Forca("gato", max_erros=3)
        for c in "xyz":
            self.assertFalse(f.chutar(c))
        self.assertTrue(f.perdeu)
        with self.assertRaises(RuntimeError):
            f.chutar("g")

    def test_repetido_nao_penaliza(self):
        f = Forca("gato")
        f.chutar("x")
        f.chutar("x")
        self.assertEqual(f.erros, ["x"])

    def test_acentos(self):
        f = Forca("coração")
        f.chutar("a")
        self.assertIn("ã", f.mascara)

    def test_sortear_seed(self):
        p = ["a", "bb", "cc", "dd"]
        a = Forca.sortear(p, random.Random(3)).palavra
        b = Forca.sortear(p, random.Random(3)).palavra
        self.assertEqual(a, b)

    def test_invalido(self):
        with self.assertRaises(ValueError):
            Forca("")
        with self.assertRaises(ValueError):
            Forca("abc").chutar("ab")


if __name__ == "__main__":
    unittest.main()
