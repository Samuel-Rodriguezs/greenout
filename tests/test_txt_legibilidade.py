import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from txt_legibilidade import classificar, flesch_pt, nivel_texto


class TestLegibilidade(unittest.TestCase):
    def test_formula(self):
        # 2 palavras, 1 sentença, 4 sílabas -> 248,835 - 2,03 - 169,2
        self.assertAlmostEqual(flesch_pt("casa bola."), 248.835 - 1.015 * 2 - 84.6 * 2)

    def test_facil_vs_dificil(self):
        facil = "O gato é bom. Ele dá o pão."
        dificil = ("A implementação extraordinariamente complicada requer conhecimentos "
                   "especializados considerabilíssimos.")
        self.assertGreater(flesch_pt(facil), flesch_pt(dificil))
        self.assertEqual(nivel_texto(facil), "muito fácil")

    def test_classificar_limites(self):
        self.assertEqual(classificar(75), "muito fácil")
        self.assertEqual(classificar(50), "fácil")
        self.assertEqual(classificar(25), "difícil")
        self.assertEqual(classificar(24.9), "muito difícil")

    def test_sem_palavras(self):
        with self.assertRaises(ValueError):
            flesch_pt("... 123")


if __name__ == "__main__":
    unittest.main()
