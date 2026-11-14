import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from gr_pontes import pontes_e_articulacoes


class TestPontes(unittest.TestCase):
    def test_triangulo_com_cauda(self):
        pontes, art = pontes_e_articulacoes(5, [(0, 1), (1, 2), (2, 0), (1, 3), (3, 4)])
        self.assertEqual(pontes, [(1, 3), (3, 4)])
        self.assertEqual(art, {1, 3})

    def test_ciclo_sem_pontes(self):
        pontes, art = pontes_e_articulacoes(4, [(0, 1), (1, 2), (2, 3), (3, 0)])
        self.assertEqual((pontes, art), ([], set()))

    def test_raiz_articulacao(self):
        pontes, art = pontes_e_articulacoes(3, [(0, 1), (0, 2)])
        self.assertEqual(pontes, [(0, 1), (0, 2)])
        self.assertEqual(art, {0})

    def test_aresta_paralela_nao_e_ponte(self):
        pontes, _ = pontes_e_articulacoes(2, [(0, 1), (0, 1)])
        self.assertEqual(pontes, [])

    def test_desconexo_e_vazio(self):
        self.assertEqual(pontes_e_articulacoes(0, []), ([], set()))
        self.assertEqual(pontes_e_articulacoes(4, [(0, 1), (2, 3)]), ([(0, 1), (2, 3)], set()))

    def test_caminho_longo(self):
        n = 3000
        pontes, art = pontes_e_articulacoes(n, [(i, i + 1) for i in range(n - 1)])
        self.assertEqual(len(pontes), n - 1)
        self.assertEqual(len(art), n - 2)


if __name__ == "__main__":
    unittest.main()
