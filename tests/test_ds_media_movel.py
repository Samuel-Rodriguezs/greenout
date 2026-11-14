import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

import ds_media_movel as m


class TestMediaMovel(unittest.TestCase):
    def test_simples(self):
        r = m.media_movel([1, 2, 3, 4, 5], 3)
        self.assertEqual(len(r), 3)
        for a, b in zip(r, [2.0, 3.0, 4.0]):
            self.assertAlmostEqual(a, b)

    def test_janela_invalida(self):
        with self.assertRaises(ValueError):
            m.media_movel([1, 2], 0)
        with self.assertRaises(ValueError):
            m.media_movel([1, 2], 3)

    def test_ponderada(self):
        # (1*1 + 2*2 + 3*3)/6 = 14/6 ; (1*2 + 2*3 + 3*4)/6 = 20/6
        r = m.media_movel_ponderada([1, 2, 3, 4], [1, 2, 3])
        self.assertAlmostEqual(r[0], 14 / 6)
        self.assertAlmostEqual(r[1], 20 / 6)

    def test_exponencial(self):
        r = m.suavizacao_exponencial([10, 20, 30], 0.5)
        for a, b in zip(r, [10, 15, 22.5]):
            self.assertAlmostEqual(a, b)
        self.assertEqual(m.suavizacao_exponencial([3, 9], 1.0), [3.0, 9.0])

    def test_exponencial_invalida(self):
        with self.assertRaises(ValueError):
            m.suavizacao_exponencial([1], 0)
        with self.assertRaises(ValueError):
            m.suavizacao_exponencial([], 0.5)

    def test_holt_serie_linear(self):
        prev = m.holt([1, 2, 3, 4, 5], 0.5, 0.5, horizonte=2)
        self.assertAlmostEqual(prev[0], 6.0)
        self.assertAlmostEqual(prev[1], 7.0)


if __name__ == "__main__":
    unittest.main()
