import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from gr_coloracao import colorir, coloracao_valida, numero_cores


class TestColoracao(unittest.TestCase):
    def test_triangulo_precisa_de_3(self):
        g = {"a": ["b", "c"], "b": ["c"], "c": []}
        cor = colorir(g)
        self.assertTrue(coloracao_valida(g, cor))
        self.assertEqual(numero_cores(cor), 3)

    def test_ciclo_par_2_cores(self):
        g = {1: [2], 2: [3], 3: [4], 4: [1]}
        cor = colorir(g)
        self.assertTrue(coloracao_valida(g, cor))
        self.assertEqual(numero_cores(cor), 2)

    def test_vazio_e_isolado(self):
        self.assertEqual(colorir({}), {})
        self.assertEqual(numero_cores({}), 0)
        self.assertEqual(colorir({"x": []}), {"x": 0})

    def test_auto_laco(self):
        with self.assertRaises(ValueError):
            colorir({"a": ["a"]})

    def test_estrela(self):
        g = {0: [1, 2, 3, 4]}
        cor = colorir(g)
        self.assertEqual(numero_cores(cor), 2)
        self.assertTrue(coloracao_valida(g, cor))


if __name__ == "__main__":
    unittest.main()
