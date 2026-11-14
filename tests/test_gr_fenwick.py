import random
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from gr_fenwick import Fenwick


class TestFenwick(unittest.TestCase):
    def test_construcao_e_prefixo(self):
        f = Fenwick([3, 2, -1, 6, 5])
        self.assertEqual([f.prefixo(i) for i in range(6)], [0, 3, 5, 4, 10, 15])

    def test_somar_e_intervalo(self):
        f = Fenwick(5)
        f.somar(2, 7)
        f.somar(4, 1)
        self.assertEqual(f.intervalo(2, 5), 8)
        self.assertEqual(f.intervalo(0, 2), 0)
        self.assertEqual(f.intervalo(3, 3), 0)

    def test_erros(self):
        f = Fenwick(3)
        with self.assertRaises(IndexError):
            f.somar(3, 1)
        with self.assertRaises(IndexError):
            f.prefixo(4)
        with self.assertRaises(IndexError):
            f.intervalo(2, 1)

    def test_vazio(self):
        f = Fenwick()
        self.assertEqual(len(f), 0)
        self.assertEqual(f.prefixo(0), 0)
        self.assertEqual(f.menor_indice_com_prefixo(1), -1)

    def test_busca_por_prefixo(self):
        f = Fenwick([1, 0, 2, 3])
        self.assertEqual(f.menor_indice_com_prefixo(1), 0)
        self.assertEqual(f.menor_indice_com_prefixo(2), 2)
        self.assertEqual(f.menor_indice_com_prefixo(6), 3)
        self.assertEqual(f.menor_indice_com_prefixo(7), -1)

    def test_aleatorio(self):
        rnd = random.Random(3)
        ref = [rnd.randint(0, 9) for _ in range(50)]
        f = Fenwick(ref)
        for _ in range(200):
            i, d = rnd.randrange(50), rnd.randint(-3, 3)
            ref[i] += d
            f.somar(i, d)
            k = rnd.randint(0, 50)
            self.assertEqual(f.prefixo(k), sum(ref[:k]))


if __name__ == "__main__":
    unittest.main()
