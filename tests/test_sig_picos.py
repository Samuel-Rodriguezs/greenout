import math
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

import sig_picos as p


class TestPicos(unittest.TestCase):
    def test_basico(self):
        self.assertEqual(p.picos([0, 2, 1, 3, 0]), [1, 3])

    def test_bordas_nao_sao_picos(self):
        self.assertEqual(p.picos([5, 1, 5]), [])
        self.assertEqual(p.picos([]), [])
        self.assertEqual(p.picos([1, 2]), [])

    def test_plato(self):
        self.assertEqual(p.picos([0, 3, 3, 3, 0]), [2])
        self.assertEqual(p.picos([0, 3, 3, 4]), [])

    def test_altura(self):
        self.assertEqual(p.picos([0, 2, 0, 5, 0], altura_min=3), [3])

    def test_distancia_prefere_mais_alto(self):
        x = [0, 4, 0, 5, 0, 0, 0, 3, 0]
        self.assertEqual(p.picos(x, distancia_min=3), [3, 7])
        self.assertEqual(p.picos(x), [1, 3, 7])

    def test_proeminencia(self):
        x = [0, 5, 4, 4.5, 0]
        self.assertAlmostEqual(p.proeminencia(x, 3), 0.5)
        self.assertEqual(p.picos(x, proeminencia_min=1), [1])

    def test_vales(self):
        self.assertEqual(p.vales([3, 1, 2, 0, 4]), [1, 3])

    def test_seno(self):
        x = [math.sin(2 * math.pi * i / 20) for i in range(100)]
        self.assertEqual(p.picos(x), [5, 25, 45, 65, 85])

    def test_distancia_invalida(self):
        with self.assertRaises(ValueError):
            p.picos([1, 2, 1], distancia_min=0)


if __name__ == "__main__":
    unittest.main()
