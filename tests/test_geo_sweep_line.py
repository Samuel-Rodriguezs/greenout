import itertools
import random
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from geo_segmentos import segmentos_se_cruzam
from geo_sweep_line import existe_intersecao, pares_que_se_cruzam


class TestSweepLine(unittest.TestCase):
    def test_sem_segmentos(self):
        self.assertEqual(pares_que_se_cruzam([]), [])
        self.assertFalse(existe_intersecao([]))

    def test_x_central(self):
        segs = [((0, 0), (4, 4)), ((0, 4), (4, 0)), ((10, 0), (12, 0))]
        self.assertEqual(pares_que_se_cruzam(segs), [(0, 1)])
        self.assertTrue(existe_intersecao(segs))

    def test_paralelos_nao_cruzam(self):
        segs = [((0, 0), (5, 0)), ((0, 1), (5, 1)), ((0, 2), (5, 2))]
        self.assertEqual(pares_que_se_cruzam(segs), [])
        self.assertFalse(existe_intersecao(segs))

    def test_encostar_no_mesmo_x(self):
        # um termina em x=3 e o outro começa em x=3: contam se tocam
        segs = [((0, 0), (3, 3)), ((3, 3), (6, 0))]
        self.assertEqual(pares_que_se_cruzam(segs), [(0, 1)])

    def test_extremos_em_x_igual_mas_disjuntos(self):
        segs = [((0, 0), (3, 0)), ((3, 5), (6, 5))]
        self.assertEqual(pares_que_se_cruzam(segs), [])

    def test_vertical_e_horizontal(self):
        segs = [((2, -5), (2, 5)), ((0, 0), (4, 0)), ((7, -5), (7, 5))]
        self.assertEqual(pares_que_se_cruzam(segs), [(0, 1)])

    def test_segmentos_dados_invertidos(self):
        segs = [((4, 4), (0, 0)), ((4, 0), (0, 4))]
        self.assertEqual(pares_que_se_cruzam(segs), [(0, 1)])

    def test_colineares_sobrepostos(self):
        segs = [((0, 0), (4, 0)), ((2, 0), (8, 0)), ((9, 0), (10, 0))]
        self.assertEqual(pares_que_se_cruzam(segs), [(0, 1)])

    def test_aleatorio_igual_forca_bruta(self):
        rng = random.Random(9)
        for _ in range(40):
            segs = [
                ((rng.randint(0, 12), rng.randint(0, 12)), (rng.randint(0, 12), rng.randint(0, 12)))
                for _ in range(rng.randint(0, 14))
            ]
            esperado = sorted(
                (i, j)
                for i, j in itertools.combinations(range(len(segs)), 2)
                if segmentos_se_cruzam(*segs[i], *segs[j])
            )
            self.assertEqual(pares_que_se_cruzam(segs), esperado)
            self.assertEqual(existe_intersecao(segs), bool(esperado))


if __name__ == "__main__":
    unittest.main()
