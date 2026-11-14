import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "python"))

from alg_intervalos import mesclar_intervalos


class TesteIntervalos(unittest.TestCase):
    def test_exemplo_classico(self):
        self.assertEqual(
            mesclar_intervalos([(1, 3), (2, 6), (8, 10), (15, 18)]),
            [(1, 6), (8, 10), (15, 18)],
        )

    def test_vazio(self):
        self.assertEqual(mesclar_intervalos([]), [])

    def test_um_intervalo(self):
        self.assertEqual(mesclar_intervalos([(1, 2)]), [(1, 2)])

    def test_tocando_nas_pontas(self):
        self.assertEqual(mesclar_intervalos([(1, 4), (4, 5)]), [(1, 5)])

    def test_desordenados(self):
        self.assertEqual(mesclar_intervalos([(5, 6), (1, 2), (2, 3)]), [(1, 3), (5, 6)])

    def test_contido(self):
        self.assertEqual(mesclar_intervalos([(1, 10), (2, 3), (4, 5)]), [(1, 10)])

    def test_pontuais_e_duplicados(self):
        self.assertEqual(mesclar_intervalos([(3, 3), (3, 3), (4, 4)]), [(3, 3), (4, 4)])

    def test_nao_altera_entrada(self):
        entrada = [(5, 6), (1, 2)]
        mesclar_intervalos(entrada)
        self.assertEqual(entrada, [(5, 6), (1, 2)])

    def test_invalido(self):
        with self.assertRaises(ValueError):
            mesclar_intervalos([(3, 1)])


if __name__ == "__main__":
    unittest.main()
