import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from mat_estatistica import desvio_padrao, media, mediana, moda, variancia


class TestEstatistica(unittest.TestCase):
    def test_media(self):
        self.assertAlmostEqual(media([1, 2, 3, 4]), 2.5)

    def test_mediana(self):
        self.assertEqual(mediana([3, 1, 2]), 2)
        self.assertEqual(mediana([4, 1, 3, 2]), 2.5)
        self.assertEqual(mediana([7]), 7)

    def test_moda(self):
        self.assertEqual(moda([1, 2, 2, 3]), [2])
        self.assertEqual(moda([1, 1, 2, 2, 3]), [1, 2])

    def test_variancia_desvio(self):
        d = [2, 4, 4, 4, 5, 5, 7, 9]
        self.assertAlmostEqual(variancia(d), 4.0)
        self.assertAlmostEqual(desvio_padrao(d), 2.0)
        self.assertAlmostEqual(variancia([1, 2, 3, 4], amostral=True), 5 / 3)

    def test_erros(self):
        for f in (media, mediana, moda, variancia):
            with self.assertRaises(ValueError):
                f([])
        with self.assertRaises(ValueError):
            variancia([1], amostral=True)


if __name__ == "__main__":
    unittest.main()
