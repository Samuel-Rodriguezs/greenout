import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from sim_langton import FormigaLangton


class TestLangton(unittest.TestCase):
    def test_primeiros_passos(self):
        f = FormigaLangton(11, 11)
        f.passo()
        self.assertEqual(f.pretas, {(5, 5)})
        self.assertEqual(f.pos, (5, 6))
        self.assertEqual(f.direcao, 1)
        f.passo()
        self.assertEqual(f.pos, (6, 6))
        self.assertEqual(f.pretas, {(5, 5), (5, 6)})

    def test_celula_preta_inverte(self):
        f = FormigaLangton(5, 5, pos=(2, 2))
        f.pretas = {(2, 2)}
        f.passo()
        self.assertNotIn((2, 2), f.pretas)
        self.assertEqual(f.direcao, 3)
        self.assertEqual(f.pos, (2, 1))

    def test_toroide(self):
        f = FormigaLangton(3, 3, pos=(0, 0), direcao=3)
        f.pretas = {(0, 0)}
        f.passo()  # vira à esquerda de oeste -> sul
        self.assertEqual(f.pos, (1, 0))
        f = FormigaLangton(3, 3, pos=(0, 0), direcao=1)
        f.pretas = {(0, 0)}
        f.passo()  # de leste, esquerda -> norte, e dá a volta
        self.assertEqual(f.pos, (2, 0))

    def test_ciclo_de_104_passos_gera_rodovia(self):
        f = FormigaLangton(80, 80)
        f.executar(11000)
        # após ~10000 passos a formiga constrói a "rodovia": padrão cresce sem parar
        self.assertGreater(len(f.pretas), 100)
        self.assertEqual(f.passos, 11000)

    def test_render_consistente_com_estado(self):
        f = FormigaLangton(9, 9)
        f.executar(10)
        self.assertEqual(sum(row.count("#") for row in f.render()), len(f.pretas - {f.pos}))

    def test_render(self):
        f = FormigaLangton(3, 3)
        self.assertEqual(f.render(), ["...", ".@.", "..."])


if __name__ == "__main__":
    unittest.main()
