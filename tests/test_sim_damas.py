import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from sim_damas import Damas


def jogo(pecas, vez="b"):
    d = Damas()
    d.tab = dict(pecas)
    d.vez = vez
    return d


class TestDamas(unittest.TestCase):
    def test_inicio(self):
        d = Damas()
        self.assertEqual(sum(1 for p in d.tab.values() if p == "b"), 12)
        self.assertEqual(sum(1 for p in d.tab.values() if p == "p"), 12)
        self.assertEqual(len(d.jogadas_legais()), 7)

    def test_movimento_simples_alterna_vez(self):
        d = Damas()
        d.mover((5, 0), (4, 1))
        self.assertEqual(d.vez, "p")
        self.assertEqual(d.tab[(4, 1)], "b")

    def test_captura_obrigatoria(self):
        d = jogo({(5, 2): "b", (4, 3): "p", (7, 0): "b"})
        self.assertEqual(d.jogadas_legais(), [((5, 2), (3, 4))])
        with self.assertRaises(ValueError):
            d.mover((7, 0), (6, 1))
        d.mover((5, 2), (3, 4))
        self.assertNotIn((4, 3), d.tab)

    def test_captura_multipla(self):
        d = jogo({(6, 1): "b", (5, 2): "p", (3, 4): "p"})
        continua = d.mover((6, 1), (4, 3))
        self.assertTrue(continua)
        self.assertEqual(d.vez, "b")
        continua = d.mover((4, 3), (2, 5))
        self.assertFalse(continua)
        self.assertEqual(d.vencedor, "b")

    def test_promocao_e_dama(self):
        d = jogo({(1, 2): "b", (1, 6): "p"})
        d.mover((1, 2), (0, 1))
        self.assertEqual(d.tab[(0, 1)], "B")
        d.mover((1, 6), (2, 5))
        movs = [dest for orig, dest in d.jogadas_legais() if orig == (0, 1)]
        self.assertIn((1, 0), movs)
        self.assertIn((1, 2), movs)

    def test_peca_comum_nao_anda_para_tras(self):
        d = jogo({(4, 3): "b", (0, 1): "p"})
        destinos = [dest for _, dest in d.jogadas_legais()]
        self.assertEqual(sorted(destinos), [(3, 2), (3, 4)])


if __name__ == "__main__":
    unittest.main()
