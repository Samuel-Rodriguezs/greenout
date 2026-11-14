import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from ecs_animacao import Animacao, SpriteSheet


class TestAnimacao(unittest.TestCase):
    def test_loop(self):
        a = Animacao([0, 1, 2], 0.1)
        vistos = []
        for _ in range(7):
            vistos.append(a.quadro)
            a.avancar(0.1)
        self.assertEqual(vistos, [0, 1, 2, 0, 1, 2, 0])

    def test_uma_vez_trava_no_ultimo(self):
        a = Animacao([4, 5], 0.5, "uma_vez")
        self.assertFalse(a.terminou)
        a.avancar(0.5)
        self.assertEqual(a.quadro, 5)
        self.assertFalse(a.terminou)
        a.avancar(10)
        self.assertEqual(a.quadro, 5)
        self.assertTrue(a.terminou)
        a.reiniciar()
        self.assertEqual((a.quadro, a.terminou), (4, False))

    def test_vai_e_volta(self):
        a = Animacao([0, 1, 2, 3], 1.0, "vai_e_volta")
        vistos = []
        for _ in range(8):
            vistos.append(a.quadro)
            a.avancar(1.0)
        self.assertEqual(vistos, [0, 1, 2, 3, 2, 1, 0, 1])
        self.assertEqual(a.duracao_total, 6.0)

    def test_vai_e_volta_curto(self):
        a = Animacao([7, 8], 1.0, "vai_e_volta")
        self.assertEqual(a.duracao_total, 2.0)

    def test_dt_grande_pula_quadros(self):
        a = Animacao([0, 1, 2, 3], 0.1)
        a.avancar(0.25)
        self.assertEqual(a.quadro, 2)
        a.avancar(0.35)  # 0.6 mod 0.4 = 0.2
        self.assertEqual(a.quadro, 2)

    def test_sprite_sheet(self):
        s = SpriteSheet(4, 2, 32, 48)
        self.assertEqual(s.retangulo(0), (0, 0, 32, 48))
        self.assertEqual(s.retangulo(5), (32, 48, 32, 48))
        with self.assertRaises(IndexError):
            s.retangulo(8)

    def test_invalidos(self):
        with self.assertRaises(ValueError):
            Animacao([], 1)
        with self.assertRaises(ValueError):
            Animacao([0], 0)
        with self.assertRaises(ValueError):
            Animacao([0], 1, "xyz")  # type: ignore[arg-type]
        with self.assertRaises(ValueError):
            Animacao([0], 1).avancar(-1)


if __name__ == "__main__":
    unittest.main()
