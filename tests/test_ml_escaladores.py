import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from ml_escaladores import Normalizador, Padronizador

X = [[1.0, 10.0], [2.0, 20.0], [3.0, 30.0], [4.0, 40.0]]


class TestEscaladores(unittest.TestCase):
    def test_padronizador_media_zero_desvio_um(self):
        Z = Padronizador().ajustar_transformar(X)
        for col in zip(*Z):
            self.assertAlmostEqual(sum(col) / len(col), 0.0)
            self.assertAlmostEqual(sum(v * v for v in col) / len(col), 1.0)

    def test_padronizador_usa_parametros_do_treino(self):
        p = Padronizador().ajustar(X)
        self.assertAlmostEqual(p.transformar([[2.5, 25.0]])[0][0], 0.0)
        self.assertGreater(p.transformar([[100.0, 0.0]])[0][0], 10)

    def test_coluna_constante(self):
        self.assertEqual(Padronizador().ajustar_transformar([[5.0], [5.0]]), [[0.0], [0.0]])
        self.assertEqual(Normalizador().ajustar_transformar([[5.0], [5.0]]), [[0.0], [0.0]])

    def test_normalizador_01(self):
        N = Normalizador().ajustar_transformar(X)
        self.assertEqual(N[0], [0.0, 0.0])
        self.assertEqual(N[-1], [1.0, 1.0])
        self.assertAlmostEqual(N[1][0], 1 / 3)

    def test_intervalo_customizado(self):
        N = Normalizador(-1, 1).ajustar_transformar(X)
        self.assertEqual(N[0][0], -1.0)
        self.assertEqual(N[-1][0], 1.0)

    def test_inversao(self):
        n = Normalizador(-1, 1).ajustar(X)
        for a, b in zip(n.inverter(n.transformar(X)), X):
            self.assertEqual([round(v, 9) for v in a], b)
        p = Padronizador().ajustar(X)
        for a, b in zip(p.inverter(p.transformar(X)), X):
            self.assertEqual([round(v, 9) for v in a], b)

    def test_erros(self):
        with self.assertRaises(RuntimeError):
            Padronizador().transformar(X)
        with self.assertRaises(RuntimeError):
            Normalizador().transformar(X)
        with self.assertRaises(ValueError):
            Normalizador(1, 1)
        with self.assertRaises(ValueError):
            Padronizador().ajustar([])


if __name__ == "__main__":
    unittest.main()
