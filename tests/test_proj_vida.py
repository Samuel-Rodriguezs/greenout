import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from proj_vida import proxima_geracao, simular, de_texto, para_texto


class TestVida(unittest.TestCase):
    def test_bloco_estavel(self):
        bloco = {(0, 0), (1, 0), (0, 1), (1, 1)}
        self.assertEqual(proxima_geracao(bloco), frozenset(bloco))

    def test_blinker_oscila(self):
        h = {(0, 1), (1, 1), (2, 1)}
        v = frozenset({(1, 0), (1, 1), (1, 2)})
        self.assertEqual(proxima_geracao(h), v)
        self.assertEqual(simular(h, 2), frozenset(h))

    def test_planador_desloca(self):
        p = de_texto(".#.\n..#\n###")
        self.assertEqual(simular(p, 4), frozenset((x + 1, y + 1) for x, y in p))

    def test_celula_solitaria_morre(self):
        self.assertEqual(proxima_geracao({(0, 0)}), frozenset())

    def test_texto_ida_e_volta(self):
        txt = ".#.\n###\n.#."
        self.assertEqual(para_texto(de_texto(txt)), txt)
        self.assertEqual(para_texto([]), "")

    def test_geracoes_negativas(self):
        with self.assertRaises(ValueError):
            simular({(0, 0)}, -1)


if __name__ == "__main__":
    unittest.main()
