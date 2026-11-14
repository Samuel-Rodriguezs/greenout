import random
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from puz_ponte_lanterna import solucao_dijkstra, tempo_minimo


class TestPonteLanterna(unittest.TestCase):
    def test_classico_1_2_5_10(self):
        self.assertEqual(tempo_minimo([1, 2, 5, 10]), 17)

    def test_bordas(self):
        self.assertEqual(tempo_minimo([]), 0)
        self.assertEqual(tempo_minimo([7]), 7)
        self.assertEqual(tempo_minimo([3, 8]), 8)
        self.assertEqual(tempo_minimo([1, 2, 5]), 8)

    def test_ordem_nao_importa(self):
        self.assertEqual(tempo_minimo([10, 1, 5, 2]), 17)

    def test_dijkstra_confere_classico(self):
        tempo, passos = solucao_dijkstra([1, 2, 5, 10])
        self.assertEqual(tempo, 17)
        self.assertEqual(len(passos), 5)
        self.assertEqual(sum(max(p[1]) for p in passos), 17)

    def test_dijkstra_concorda_com_formula(self):
        rng = random.Random(7)
        for _ in range(25):
            t = [rng.randint(1, 20) for _ in range(rng.randint(1, 6))]
            self.assertEqual(solucao_dijkstra(t)[0], tempo_minimo(t), t)

    def test_vazio(self):
        self.assertEqual(solucao_dijkstra([]), (0, []))

    def test_invalido(self):
        with self.assertRaises(ValueError):
            tempo_minimo([1, 0])


if __name__ == "__main__":
    unittest.main()
