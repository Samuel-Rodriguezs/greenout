import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from kata_kaprekar import eh_kaprekar, passo, passos_ate_6174


class TestKataKaprekar(unittest.TestCase):
    def test_passo(self):
        self.assertEqual(passo(3524), 5432 - 2345)
        self.assertEqual(passo(6174), 6174)

    def test_passo_com_zeros(self):
        self.assertEqual(passo(1000), 1000 - 1)
        self.assertEqual(passo(12), 2100 - 12)

    def test_sequencia_classica(self):
        self.assertEqual(passo(3524), 3087)
        self.assertEqual(passo(3087), 8352)
        self.assertEqual(passo(8352), 6174)

    def test_passos(self):
        self.assertEqual(passos_ate_6174(6174), 0)
        self.assertEqual(passos_ate_6174(3524), 3)
        self.assertEqual(passos_ate_6174(1000), 5)

    def test_converge_em_ate_sete(self):
        for n in range(10000):
            if len(set(f"{n:04d}")) > 1:
                self.assertLessEqual(passos_ate_6174(n), 7, n)

    def test_digitos_iguais(self):
        for n in (0, 1111, 9999):
            with self.assertRaises(ValueError):
                passos_ate_6174(n)

    def test_fora_do_intervalo(self):
        with self.assertRaises(ValueError):
            passo(10000)
        with self.assertRaises(ValueError):
            passo(-1)

    def test_numeros_de_kaprekar(self):
        esperados = [1, 9, 45, 55, 99, 297, 703, 999, 2223, 2728, 4879, 4950, 5050]
        encontrados = [n for n in range(1, 5100) if eh_kaprekar(n)]
        self.assertEqual(encontrados, esperados)

    def test_kaprekar_invalido(self):
        with self.assertRaises(ValueError):
            eh_kaprekar(0)


if __name__ == "__main__":
    unittest.main()
