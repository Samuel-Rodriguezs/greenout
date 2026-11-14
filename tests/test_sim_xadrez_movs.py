import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from sim_xadrez_movs import Tabuleiro, casa_de_nome, menor_caminho_cavalo, nome_da_casa


class TestXadrezMovs(unittest.TestCase):
    def test_nomes(self):
        self.assertEqual(casa_de_nome("e4"), (4, 3))
        self.assertEqual(nome_da_casa((0, 0)), "a1")
        with self.assertRaises(ValueError):
            casa_de_nome("i9")

    def test_cavalo_centro_e_canto(self):
        t = Tabuleiro({casa_de_nome("d4"): ("B", "C"), casa_de_nome("a1"): ("P", "C")})
        self.assertEqual(len(t.movimentos(casa_de_nome("d4"))), 8)
        self.assertEqual([nome_da_casa(c) for c in t.movimentos(casa_de_nome("a1"))], ["b3", "c2"])

    def test_cavalo_nao_captura_aliado_mas_captura_inimigo(self):
        t = Tabuleiro({(1, 0): ("B", "C"), (2, 2): ("B", "T"), (0, 2): ("P", "T")})
        destinos = t.movimentos((1, 0))
        self.assertNotIn((2, 2), destinos)
        self.assertIn((0, 2), destinos)

    def test_torre_livre(self):
        t = Tabuleiro({(0, 0): ("B", "T")})
        self.assertEqual(len(t.movimentos((0, 0))), 14)

    def test_torre_bloqueios(self):
        t = Tabuleiro({(0, 0): ("B", "T"), (0, 3): ("B", "C"), (3, 0): ("P", "C")})
        m = t.movimentos((0, 0))
        self.assertIn((3, 0), m)
        self.assertNotIn((4, 0), m)
        self.assertIn((0, 2), m)
        self.assertNotIn((0, 3), m)

    def test_mover_e_capturar(self):
        t = Tabuleiro({(0, 0): ("B", "T"), (0, 5): ("P", "C")})
        self.assertEqual(t.mover((0, 0), (0, 5)), ("P", "C"))
        self.assertEqual(t.pecas, {(0, 5): ("B", "T")})
        with self.assertRaises(ValueError):
            t.mover((0, 5), (1, 6))
        with self.assertRaises(ValueError):
            t.movimentos((7, 7))

    def test_menor_caminho(self):
        self.assertEqual(menor_caminho_cavalo((0, 0), (0, 0)), 0)
        self.assertEqual(menor_caminho_cavalo((0, 0), (1, 2)), 1)
        self.assertEqual(menor_caminho_cavalo((0, 0), (7, 7)), 6)
        self.assertEqual(menor_caminho_cavalo((0, 0), (1, 1)), 4)


if __name__ == "__main__":
    unittest.main()
