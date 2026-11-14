import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from sim_hanoi_jogo import HanoiJogo


class TestHanoiJogo(unittest.TestCase):
    def test_estado_inicial(self):
        h = HanoiJogo(3)
        self.assertEqual(h.pinos, [[3, 2, 1], [], []])
        self.assertEqual(h.minimo, 7)

    def test_jogadas_invalidas(self):
        h = HanoiJogo(3)
        with self.assertRaises(ValueError):
            h.mover(1, 2)
        h.mover(0, 1)
        with self.assertRaises(ValueError):
            h.mover(0, 1)
        with self.assertRaises(ValueError):
            h.mover(0, 0)
        with self.assertRaises(ValueError):
            h.mover(0, 5)

    def test_dicas_resolvem_no_minimo(self):
        for n in range(1, 7):
            h = HanoiJogo(n)
            while not h.venceu:
                h.mover(*h.dica())
            self.assertEqual(h.jogadas, h.minimo)
            self.assertIsNone(h.dica())

    def test_dica_apos_jogada_ruim(self):
        h = HanoiJogo(3)
        h.mover(0, 2)
        h.mover(0, 1)
        while not h.venceu:
            h.mover(*h.dica())
        self.assertTrue(h.venceu)

    def test_zero_discos(self):
        with self.assertRaises(ValueError):
            HanoiJogo(0)


if __name__ == "__main__":
    unittest.main()
