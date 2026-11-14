import random
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from puz_lights_out import aplicar, dimensao_do_nucleo, resolver


class TestLightsOut(unittest.TestCase):
    def test_ja_apagado(self):
        self.assertEqual(resolver([[0, 0], [0, 0]]), [[0, 0], [0, 0]])

    def test_vazio(self):
        self.assertEqual(resolver([]), [])

    def test_todas_acesas_3x3(self):
        luzes = [[1] * 3 for _ in range(3)]
        sol = resolver(luzes)
        self.assertEqual(sol, [[1, 0, 1], [0, 1, 0], [1, 0, 1]])
        self.assertEqual(aplicar(luzes, sol), [[0] * 3] * 3)

    def test_uma_luz_1x1(self):
        self.assertEqual(resolver([[1]]), [[1]])

    def test_5x5_sempre_resolve_embaralhado_por_botoes(self):
        rng = random.Random(11)
        for _ in range(10):
            botoes = [[rng.randint(0, 1) for _ in range(5)] for _ in range(5)]
            luzes = aplicar([[0] * 5 for _ in range(5)], botoes)
            sol = resolver(luzes)
            self.assertIsNotNone(sol)
            self.assertEqual(aplicar(luzes, sol), [[0] * 5 for _ in range(5)])

    def test_5x5_tem_nucleo_de_dimensao_2(self):
        self.assertEqual(dimensao_do_nucleo(5, 5), 2)
        self.assertEqual(dimensao_do_nucleo(3, 3), 0)

    def test_sem_solucao_5x5(self):
        # no 5x5 só 1/4 das configurações é resolúvel (núcleo de dimensão 2)
        luzes = [[0] * 5 for _ in range(5)]
        luzes[0][1] = 1
        self.assertIsNone(resolver(luzes))

    def test_2x2(self):
        luzes = [[1, 0], [0, 0]]
        sol = resolver(luzes)
        self.assertEqual(aplicar(luzes, sol), [[0, 0], [0, 0]])


if __name__ == "__main__":
    unittest.main()
