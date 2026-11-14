import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from ecs_tilemap import Tilemap


class TestTilemap(unittest.TestCase):
    def setUp(self):
        self.m = Tilemap(10, 8, 16)
        self.m.adicionar_camada("chao", 1)
        self.m.adicionar_camada("objetos")

    def test_camadas_e_visivel(self):
        self.assertEqual(self.m.camadas(), ["chao", "objetos"])
        self.assertEqual(self.m.tile_visivel(2, 2), 1)
        self.m.definir("objetos", 2, 2, 7)
        self.assertEqual(self.m.tile_visivel(2, 2), 7)
        self.assertEqual(self.m.obter("chao", 2, 2), 1)

    def test_limites(self):
        with self.assertRaises(IndexError):
            self.m.obter("chao", 10, 0)
        with self.assertRaises(IndexError):
            self.m.definir("chao", -1, 0, 3)
        with self.assertRaises(ValueError):
            self.m.adicionar_camada("chao")
        with self.assertRaises(ValueError):
            Tilemap(0, 5)

    def test_solidos_em_qualquer_camada_e_fora(self):
        self.m.definir_solidos({9})
        self.assertFalse(self.m.solido(1, 1))
        self.m.definir("chao", 1, 1, 9)
        self.m.definir("objetos", 3, 3, 9)
        self.assertTrue(self.m.solido(1, 1))
        self.assertTrue(self.m.solido(3, 3))
        self.assertTrue(self.m.solido(-1, 0))
        self.assertTrue(self.m.solido(0, 8))

    def test_coordenadas(self):
        self.assertEqual(self.m.mundo_para_tile(33.5, 15.9), (2, 0))
        self.assertEqual(self.m.mundo_para_tile(-0.5, -16), (-1, -1))
        self.assertEqual(self.m.tile_para_mundo(3, 2), (48, 32))

    def test_janela(self):
        self.assertEqual(self.m.janela(0, 0, 64, 32), (0, 0, 4, 2))
        self.assertEqual(self.m.janela(8, 8, 64, 32), (0, 0, 5, 3))  # parcialmente visíveis
        self.assertEqual(self.m.janela(-100, -100, 400, 400), (0, 0, 10, 8))
        self.assertEqual(self.m.janela(1000, 0, 50, 50)[0:3:2], (10, 10))

    def test_preencher_retangulo_recorta(self):
        self.m.preencher_retangulo("objetos", 8, 6, 5, 5, 4)
        self.assertEqual(self.m.obter("objetos", 9, 7), 4)
        self.assertEqual(self.m.obter("objetos", 7, 7), 0)
        self.m.preencher_retangulo("objetos", -2, -2, 3, 3, 5)
        self.assertEqual(self.m.obter("objetos", 0, 0), 5)
        self.assertEqual(self.m.obter("objetos", 1, 1), 0)


if __name__ == "__main__":
    unittest.main()
