import random
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from sim_random_walk import (caminhada_1d, caminhada_2d, distancia_origem,
                             distancia_quadratica_media, maxima_excursao, primeiro_retorno)


class TestRandomWalk(unittest.TestCase):
    def test_1d_passos_unitarios(self):
        t = caminhada_1d(200, random.Random(1))
        self.assertEqual(len(t), 201)
        self.assertTrue(all(abs(b - a) == 1 for a, b in zip(t, t[1:])))

    def test_determinismo(self):
        self.assertEqual(caminhada_1d(50, random.Random(4)), caminhada_1d(50, random.Random(4)))
        self.assertEqual(caminhada_2d(50, random.Random(4)), caminhada_2d(50, random.Random(4)))

    def test_2d_vizinhos(self):
        t = caminhada_2d(300, random.Random(2))
        self.assertEqual(t[0], (0, 0))
        self.assertTrue(all(abs(b[0] - a[0]) + abs(b[1] - a[1]) == 1 for a, b in zip(t, t[1:])))

    def test_difusao(self):
        d2 = distancia_quadratica_media(100, 2000, random.Random(5))
        self.assertAlmostEqual(d2, 100, delta=15)

    def test_inicio_e_excursao(self):
        t = caminhada_1d(100, random.Random(3), inicio=10)
        self.assertEqual(t[0], 10)
        self.assertLessEqual(maxima_excursao(t), 100)
        self.assertEqual(maxima_excursao([0]), 0)

    def test_primeiro_retorno_par(self):
        n = primeiro_retorno(random.Random(7))
        if n is not None:
            self.assertEqual(n % 2, 0)
        self.assertIsNone(primeiro_retorno(random.Random(7), limite=1))

    def test_distancia(self):
        self.assertEqual(distancia_origem((3, 4)), 5.0)


if __name__ == "__main__":
    unittest.main()
