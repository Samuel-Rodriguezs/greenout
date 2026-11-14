import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

import sig_media_movel as m


class TestMediaMovel(unittest.TestCase):
    def test_media(self):
        self.assertEqual(m.media_movel([1, 2, 3, 4, 5], 3), [1, 1.5, 2, 3, 4])

    def test_media_janela_um(self):
        self.assertEqual(m.media_movel([4, 8], 1), [4, 8])

    def test_media_vazia_e_invalida(self):
        self.assertEqual(m.media_movel([], 3), [])
        with self.assertRaises(ValueError):
            m.media_movel([1], 0)

    def test_exponencial(self):
        self.assertEqual(m.media_exponencial([10, 0, 0], 0.5), [10, 5, 2.5])
        self.assertEqual(m.media_exponencial([1, 2, 3], 1), [1, 2, 3])
        with self.assertRaises(ValueError):
            m.media_exponencial([1], 0)

    def test_mediana_remove_espiga(self):
        self.assertEqual(m.mediana_movel([1, 1, 100, 1, 1], 3), [1, 1, 1, 1, 1])

    def test_mediana_bordas(self):
        self.assertEqual(m.mediana_movel([5, 1, 3], 3), [3, 3, 2])

    def test_mediana_invalida(self):
        with self.assertRaises(ValueError):
            m.mediana_movel([1, 2], 2)

    def test_media_suaviza(self):
        ruidoso = [0, 10] * 10
        suave = m.media_movel(ruidoso, 4)
        self.assertEqual(suave[-1], 5)


if __name__ == "__main__":
    unittest.main()
