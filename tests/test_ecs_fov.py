import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from ecs_fov import campo_visao


def mapa(linhas):
    paredes = {(x, y) for y, l in enumerate(linhas) for x, c in enumerate(l) if c == "#"}
    return lambda x, y: (x, y) in paredes or not (0 <= y < len(linhas) and 0 <= x < len(linhas[0]))


class TestFOV(unittest.TestCase):
    def test_sala_aberta_ve_tudo_no_raio(self):
        livre = lambda x, y: False
        v = campo_visao((0, 0), 3, livre)
        esperado = {(x, y) for x in range(-3, 4) for y in range(-3, 4) if x * x + y * y <= 9}
        self.assertEqual(v, esperado)

    def test_raio_zero(self):
        self.assertEqual(campo_visao((2, 2), 0, lambda x, y: False), {(2, 2)})

    def test_parede_bloqueia_atras(self):
        paredes = {(3, 1)}
        v = campo_visao((1, 1), 6, lambda x, y: (x, y) in paredes)
        self.assertIn((3, 1), v)      # a parede em si é vista
        self.assertNotIn((4, 1), v)   # sombra direta
        self.assertNotIn((5, 1), v)
        self.assertIn((4, 4), v)

    def test_corredor_com_porta(self):
        m = mapa(["#########",
                  "#.......#",
                  "#########"])
        v = campo_visao((1, 1), 10, m)
        interior = {(x, 1) for x in range(1, 8)}
        self.assertTrue(interior <= v)
        # nada além das paredes externas
        self.assertTrue(all(0 <= x < 9 and 0 <= y < 3 for x, y in v))

    def test_sala_fechada_nao_vaza(self):
        m = mapa(["#######",
                  "#..#..#",
                  "#..#..#",
                  "#######"])
        v = campo_visao((1, 1), 10, m)
        self.assertNotIn((4, 1), v)
        self.assertNotIn((5, 2), v)
        self.assertIn((3, 1), v)

    def test_pilar_projeta_sombra_so_atras(self):
        pilar = {(3, 0)}
        v = campo_visao((0, 0), 8, lambda x, y: (x, y) in pilar)
        self.assertNotIn((5, 0), v)
        self.assertIn((5, 3), v)
        self.assertIn((0, 5), v)

    def test_simetria_de_quadrantes(self):
        pilar = {(2, 2), (-2, -2)}
        v = campo_visao((0, 0), 6, lambda x, y: (x, y) in pilar)
        self.assertEqual({(x, y) for x, y in v}, {(-x, -y) for x, y in v})

    def test_raio_negativo(self):
        with self.assertRaises(ValueError):
            campo_visao((0, 0), -1, lambda x, y: False)


if __name__ == "__main__":
    unittest.main()
