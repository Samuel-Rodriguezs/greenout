import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from rede_janela import (eficiencia, go_back_n, janela_maxima_valida,
                         selective_repeat)


class TestRedeJanela(unittest.TestCase):
    def test_sem_perdas(self):
        self.assertEqual(go_back_n(6, 3), [0, 1, 2, 3, 4, 5])
        self.assertEqual(selective_repeat(6, 3), [0, 1, 2, 3, 4, 5])

    def test_gbn_perda(self):
        # quadro 2 perdido, janela 4: reenvia 2 e 3 (e 4,5 junto) na rodada seguinte
        self.assertEqual(go_back_n(6, 4, {2}), [0, 1, 2, 3, 2, 3, 4, 5])

    def test_sr_perda(self):
        # só o quadro 2 é reenviado
        self.assertEqual(selective_repeat(6, 4, {2}), [0, 1, 2, 3, 2, 4, 5])

    def test_sr_melhor_que_gbn(self):
        perdas = {1, 5}
        g, s = go_back_n(10, 4, perdas), selective_repeat(10, 4, perdas)
        self.assertLess(len(s), len(g))
        self.assertEqual(sorted(set(g)), list(range(10)))
        self.assertEqual(sorted(set(s)), list(range(10)))
        self.assertEqual(len(s), 10 + len(perdas))

    def test_perda_do_primeiro(self):
        self.assertEqual(go_back_n(3, 3, {0}), [0, 1, 2, 0, 1, 2])
        self.assertEqual(selective_repeat(3, 3, {0}), [0, 1, 2, 0])

    def test_janela_um_equivale_a_stop_and_wait(self):
        self.assertEqual(go_back_n(3, 1, {1}), [0, 1, 1, 2])
        self.assertEqual(selective_repeat(3, 1, {1}), [0, 1, 1, 2])

    def test_vazio_e_invalido(self):
        self.assertEqual(go_back_n(0, 4), [])
        self.assertEqual(selective_repeat(0, 4), [])
        with self.assertRaises(ValueError):
            go_back_n(3, 0)
        with self.assertRaises(ValueError):
            selective_repeat(-1, 2)

    def test_eficiencia(self):
        self.assertEqual(eficiencia(4, [0, 1, 2, 3]), 1.0)
        self.assertEqual(eficiencia(4, [0, 1, 2, 3, 2, 3, 2, 3]), 0.5)
        self.assertEqual(eficiencia(0, []), 1.0)

    def test_janela_maxima(self):
        self.assertEqual(janela_maxima_valida(3, "gbn"), 7)
        self.assertEqual(janela_maxima_valida(3, "sr"), 4)
        with self.assertRaises(ValueError):
            janela_maxima_valida(3, "xx")
        with self.assertRaises(ValueError):
            janela_maxima_valida(0, "gbn")


if __name__ == "__main__":
    unittest.main()
