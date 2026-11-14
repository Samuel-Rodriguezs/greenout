import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from ecs_spatial_hash import SpatialHash


class TestSpatialHash(unittest.TestCase):
    def test_consulta_exata(self):
        g = SpatialHash(10)
        g.inserir("a", 1, 1, 2, 2)
        g.inserir("b", 25, 25, 2, 2)
        self.assertEqual(g.consultar(0, 0, 5, 5), {"a"})
        self.assertEqual(g.consultar(0, 0, 100, 100), {"a", "b"})
        # mesma célula, mas fora do retângulo
        self.assertEqual(g.consultar(6, 6, 1, 1), set())

    def test_objeto_grande_ocupa_varias_celulas(self):
        g = SpatialHash(10)
        g.inserir("grande", 5, 5, 30, 4)
        self.assertEqual(g.consultar(33, 6, 1, 1), {"grande"})

    def test_mover_e_remover(self):
        g = SpatialHash(10)
        g.inserir("a", 0, 0, 1, 1)
        g.mover("a", 50, 50)
        self.assertEqual(g.consultar(0, 0, 5, 5), set())
        self.assertEqual(g.consultar(49, 49, 3, 3), {"a"})
        g.remover("a")
        self.assertEqual(len(g), 0)
        self.assertEqual(g.consultar(49, 49, 3, 3), set())
        with self.assertRaises(KeyError):
            g.remover("a")

    def test_coordenadas_negativas(self):
        g = SpatialHash(10)
        g.inserir("n", -15, -15, 2, 2)
        self.assertEqual(g.consultar(-20, -20, 10, 10), {"n"})
        self.assertEqual(g.consultar(0, 0, 5, 5), set())

    def test_pares_candidatos(self):
        g = SpatialHash(10)
        g.inserir("a", 1, 1, 1, 1)
        g.inserir("b", 5, 5, 1, 1)
        g.inserir("c", 50, 50, 1, 1)
        self.assertEqual(g.pares_candidatos(), {("a", "b")})

    def test_tamanho_invalido(self):
        with self.assertRaises(ValueError):
            SpatialHash(0)


if __name__ == "__main__":
    unittest.main()
