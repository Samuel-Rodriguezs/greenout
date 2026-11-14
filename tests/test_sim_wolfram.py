import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from sim_wolfram import proxima_geracao, renderizar, simular, tabela_regra


class TestWolfram(unittest.TestCase):
    def test_tabela_regra_30(self):
        t = tabela_regra(30)
        self.assertEqual(t[(1, 1, 1)], 0)
        self.assertEqual(t[(1, 0, 0)], 1)
        self.assertEqual(t[(0, 0, 0)], 0)
        self.assertEqual(t[(0, 0, 1)], 1)

    def test_regra_90_sierpinski(self):
        hist = simular(90, 15, 3)
        self.assertEqual(renderizar(hist).split("\n"), [
            ".......#.......",
            "......#.#......",
            ".....#...#.....",
            "....#.#.#.#....",
        ])

    def test_regra_30_primeiras_geracoes(self):
        hist = simular(30, 9, 2)
        self.assertEqual(hist[1], [0, 0, 0, 1, 1, 1, 0, 0, 0])
        self.assertEqual(hist[2], [0, 0, 1, 1, 0, 0, 1, 0, 0])

    def test_regra_0_e_255(self):
        self.assertEqual(proxima_geracao([1, 0, 1], 0), [0, 0, 0])
        self.assertEqual(proxima_geracao([1, 0, 1], 255), [1, 1, 1])

    def test_bordas(self):
        # regra 2: só (0,0,1) -> 1
        self.assertEqual(proxima_geracao([0, 0, 1], 2, circular=False), [0, 1, 0])
        self.assertEqual(proxima_geracao([1, 0, 0], 2, circular=True), [0, 0, 1])
        self.assertEqual(proxima_geracao([1, 0, 0], 2, circular=False), [0, 0, 0])

    def test_validacoes(self):
        with self.assertRaises(ValueError):
            tabela_regra(256)
        with self.assertRaises(ValueError):
            simular(30, 5, 1, [1, 0])


if __name__ == "__main__":
    unittest.main()
