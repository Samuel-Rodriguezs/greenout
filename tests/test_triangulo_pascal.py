import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "python"))

from triangulo_pascal import triangulo_pascal


class TestTrianguloPascal(unittest.TestCase):
    def test_zero_linhas(self):
        self.assertEqual(triangulo_pascal(0), [])

    def test_uma_e_duas_linhas(self):
        self.assertEqual(triangulo_pascal(1), [[1]])
        self.assertEqual(triangulo_pascal(2), [[1], [1, 1]])

    def test_cinco_linhas(self):
        self.assertEqual(
            triangulo_pascal(5),
            [[1], [1, 1], [1, 2, 1], [1, 3, 3, 1], [1, 4, 6, 4, 1]],
        )

    def test_soma_das_linhas_e_potencia_de_dois(self):
        for i, linha in enumerate(triangulo_pascal(12)):
            self.assertEqual(sum(linha), 2 ** i)

    def test_negativo(self):
        with self.assertRaises(ValueError):
            triangulo_pascal(-1)


if __name__ == "__main__":
    unittest.main()
