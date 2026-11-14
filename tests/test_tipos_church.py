import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from tipos_beta import normalizar
from tipos_church import (E_ZERO, SUC, ZERO, aplicar, de_int, para_int,
                          potencia, predecessor, produto, soma, subtracao)
from tipos_termos import alfa_equivalentes, analisar


class TestChurch(unittest.TestCase):
    def test_roundtrip(self):
        for n in range(6):
            self.assertEqual(para_int(de_int(n)), n)

    def test_negativo(self):
        with self.assertRaises(ValueError):
            de_int(-1)

    def test_zero_e_alfa_equivalente(self):
        self.assertTrue(alfa_equivalentes(ZERO, de_int(0)))

    def test_sucessor(self):
        self.assertEqual(para_int(aplicar(SUC, de_int(4))), 5)
        self.assertEqual(para_int(aplicar(SUC, ZERO)), 1)

    def test_soma(self):
        self.assertEqual(soma(2, 3), 5)
        self.assertEqual(soma(0, 0), 0)
        self.assertEqual(soma(0, 4), 4)

    def test_produto(self):
        self.assertEqual(produto(3, 4), 12)
        self.assertEqual(produto(0, 5), 0)
        self.assertEqual(produto(5, 0), 0)
        self.assertEqual(produto(1, 7), 7)

    def test_potencia(self):
        self.assertEqual(potencia(2, 5), 32)
        self.assertEqual(potencia(3, 0), 1)
        self.assertEqual(potencia(0, 3), 0)
        self.assertEqual(potencia(0, 0), 1)

    def test_predecessor(self):
        self.assertEqual(predecessor(5), 4)
        self.assertEqual(predecessor(1), 0)
        self.assertEqual(predecessor(0), 0)

    def test_subtracao_truncada(self):
        self.assertEqual(subtracao(7, 3), 4)
        self.assertEqual(subtracao(3, 7), 0)
        self.assertEqual(subtracao(4, 4), 0)

    def test_eh_zero(self):
        v = analisar("V")
        f = analisar("F")
        r0 = normalizar(aplicar(E_ZERO, de_int(0), v, f))
        r3 = normalizar(aplicar(E_ZERO, de_int(3), v, f))
        self.assertEqual(r0, v)
        self.assertEqual(r3, f)

    def test_nao_numeral(self):
        with self.assertRaises(ValueError):
            para_int(analisar("\\x.x"))
        with self.assertRaises(ValueError):
            para_int(analisar("\\f x.x f"))
        with self.assertRaises(ValueError):
            para_int(analisar("y"))


if __name__ == "__main__":
    unittest.main()
