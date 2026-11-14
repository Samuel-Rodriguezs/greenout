import random
import statistics
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from gr_mediana_fluxo import MedianaFluxo


class TestMedianaFluxo(unittest.TestCase):
    def test_vazio(self):
        with self.assertRaises(ValueError):
            MedianaFluxo().mediana()

    def test_sequencia(self):
        m = MedianaFluxo()
        esperado = []
        for x in (5, 15, 1, 3):
            m.adicionar(x)
            esperado.append(m.mediana())
        self.assertEqual(esperado, [5, 10, 5, 4])

    def test_repetidos_e_negativos(self):
        m = MedianaFluxo()
        for x in (-1, -1, -1, 2):
            m.adicionar(x)
        self.assertEqual(m.mediana(), -1)
        self.assertEqual(len(m), 4)

    def test_decimais(self):
        m = MedianaFluxo()
        m.adicionar(1.5)
        m.adicionar(2.5)
        self.assertEqual(m.mediana(), 2.0)

    def test_aleatorio(self):
        rnd = random.Random(11)
        m, ref = MedianaFluxo(), []
        for _ in range(300):
            x = rnd.randint(-100, 100)
            ref.append(x)
            m.adicionar(x)
            self.assertAlmostEqual(m.mediana(), statistics.median(ref))


if __name__ == "__main__":
    unittest.main()
