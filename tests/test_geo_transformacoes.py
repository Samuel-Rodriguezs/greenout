import math
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from geo_transformacoes import (
    IDENTIDADE,
    aplicar,
    compor,
    determinante,
    escala,
    escala_em_torno,
    inversa,
    rotacao,
    rotacao_em_torno,
    translacao,
)


def perto(testcase, p, q):
    testcase.assertAlmostEqual(p[0], q[0])
    testcase.assertAlmostEqual(p[1], q[1])


class TestTransformacoes(unittest.TestCase):
    def test_translacao_escala(self):
        self.assertEqual(aplicar(translacao(2, -1), (1, 1)), (3, 0))
        self.assertEqual(aplicar(escala(2), (1, 3)), (2, 6))
        self.assertEqual(aplicar(escala(2, 3), (1, 1)), (2, 3))

    def test_rotacao_90(self):
        perto(self, aplicar(rotacao(math.pi / 2), (1, 0)), (0, 1))
        perto(self, aplicar(rotacao(math.pi), (1, 2)), (-1, -2))

    def test_ordem_da_composicao(self):
        # rotaciona primeiro, depois translada
        m = compor(translacao(10, 0), rotacao(math.pi / 2))
        perto(self, aplicar(m, (1, 0)), (10, 1))
        # translada primeiro, depois rotaciona
        m2 = compor(rotacao(math.pi / 2), translacao(10, 0))
        perto(self, aplicar(m2, (1, 0)), (0, 11))

    def test_rotacao_em_torno_de_ponto(self):
        m = rotacao_em_torno(math.pi / 2, (1, 1))
        perto(self, aplicar(m, (2, 1)), (1, 2))
        perto(self, aplicar(m, (1, 1)), (1, 1))  # centro fixo

    def test_escala_em_torno(self):
        m = escala_em_torno(2, 2, (1, 1))
        perto(self, aplicar(m, (2, 2)), (3, 3))
        perto(self, aplicar(m, (1, 1)), (1, 1))

    def test_identidade_e_composicao_vazia(self):
        self.assertEqual(compor(), IDENTIDADE)
        self.assertEqual(aplicar(IDENTIDADE, (7, 8)), (7, 8))

    def test_determinante(self):
        self.assertEqual(determinante(escala(2, 3)), 6)
        self.assertAlmostEqual(determinante(rotacao(1.234)), 1)
        self.assertEqual(determinante(escala(0, 1)), 0)

    def test_inversa(self):
        m = compor(translacao(3, -2), rotacao(0.7), escala(2, 5))
        i = inversa(m)
        p = (4.5, -1.5)
        perto(self, aplicar(i, aplicar(m, p)), p)
        prod = compor(m, i)
        for r in range(3):
            for c in range(3):
                self.assertAlmostEqual(prod[r][c], IDENTIDADE[r][c])

    def test_inversa_singular(self):
        with self.assertRaises(ValueError):
            inversa(escala(0, 1))

    def test_ponto_no_infinito(self):
        with self.assertRaises(ValueError):
            aplicar(((1, 0, 0), (0, 1, 0), (0, 0, 0)), (1, 1))


if __name__ == "__main__":
    unittest.main()
