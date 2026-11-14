import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from ecs_raycast_dda import percorrer, raycast


class TestDDA(unittest.TestCase):
    def test_horizontal(self):
        cel = [c for c, _ in percorrer((0.5, 0.5), (1, 0), 3)]
        self.assertEqual(cel, [(0, 0), (1, 0), (2, 0), (3, 0)])

    def test_distancias_de_entrada(self):
        v = percorrer((0.5, 0.5), (1, 0), 2.4)
        self.assertEqual([c for c, _ in v], [(0, 0), (1, 0), (2, 0)])
        self.assertAlmostEqual(v[1][1], 0.5)
        self.assertAlmostEqual(v[2][1], 1.5)

    def test_negativo(self):
        cel = [c for c, _ in percorrer((0.5, 0.5), (-1, 0), 1.6)]
        self.assertEqual(cel, [(0, 0), (-1, 0), (-2, 0)])

    def test_diagonal_visita_vizinhos(self):
        cel = [c for c, _ in percorrer((0.1, 0.2), (1, 1), 3)]
        self.assertEqual(cel[0], (0, 0))
        # cada passo muda exatamente um índice
        for (a, b), (c, d) in zip(cel, cel[1:]):
            self.assertEqual(abs(a - c) + abs(b - d), 1)
        self.assertIn((2, 2), cel)

    def test_raycast_acerto_com_normal(self):
        parede = {(3, 0)}
        a = raycast((0.5, 0.5), (1, 0), 10, lambda i, j: (i, j) in parede)
        self.assertEqual(a.celula, (3, 0))
        self.assertAlmostEqual(a.distancia, 2.5)
        self.assertAlmostEqual(a.ponto[0], 3.0)
        self.assertEqual(a.normal, (-1, 0))

    def test_alcance_curto_nao_acerta(self):
        self.assertIsNone(raycast((0.5, 0.5), (1, 0), 2.0, lambda i, j: (i, j) == (3, 0)))

    def test_origem_dentro_de_bloqueio(self):
        a = raycast((0.5, 0.5), (1, 0), 5, lambda i, j: True)
        self.assertEqual((a.celula, a.distancia, a.normal), ((0, 0), 0.0, (0, 0)))

    def test_vertical_e_livre(self):
        self.assertIsNone(raycast((0.5, 0.5), (0, 1), 20, lambda i, j: False))
        a = raycast((0.5, 4.5), (0, -1), 20, lambda i, j: j == 1)
        self.assertEqual((a.celula, a.normal), ((0, 1), (0, 1)))

    def test_direcao_nula(self):
        with self.assertRaises(ValueError):
            percorrer((0, 0), (0, 0), 5)


if __name__ == "__main__":
    unittest.main()
