import random
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from gr_segment_tree import SegmentTree


class TestSegmentTree(unittest.TestCase):
    def test_soma(self):
        st = SegmentTree([1, 2, 3, 4, 5])
        self.assertEqual(st.consultar(0, 5), 15)
        self.assertEqual(st.consultar(1, 4), 9)
        self.assertEqual(st.consultar(2, 2), 0)

    def test_atualizar(self):
        st = SegmentTree([1, 2, 3])
        st.atualizar(1, 10)
        self.assertEqual(st.consultar(0, 3), 14)

    def test_minimo(self):
        st = SegmentTree([5, 2, 8, 1, 9], op=min, neutro=float("inf"))
        self.assertEqual(st.consultar(0, 3), 2)
        self.assertEqual(st.consultar(2, 5), 1)

    def test_ordem_nao_comutativa(self):
        st = SegmentTree(list("abcde"), op=lambda a, b: a + b, neutro="")
        self.assertEqual(st.consultar(0, 5), "abcde")
        self.assertEqual(st.consultar(1, 4), "bcd")

    def test_vazia_e_erros(self):
        st = SegmentTree([])
        self.assertEqual(st.consultar(0, 0), 0)
        with self.assertRaises(IndexError):
            st.atualizar(0, 1)
        with self.assertRaises(IndexError):
            SegmentTree([1]).consultar(0, 2)
        with self.assertRaises(IndexError):
            SegmentTree([1, 2]).consultar(2, 1)

    def test_aleatorio(self):
        rnd = random.Random(1)
        dados = [rnd.randint(-50, 50) for _ in range(37)]
        st = SegmentTree(dados)
        for _ in range(300):
            if rnd.random() < 0.5:
                i, v = rnd.randrange(37), rnd.randint(-50, 50)
                dados[i] = v
                st.atualizar(i, v)
            else:
                a = rnd.randint(0, 37)
                b = rnd.randint(a, 37)
                self.assertEqual(st.consultar(a, b), sum(dados[a:b]))


if __name__ == "__main__":
    unittest.main()
