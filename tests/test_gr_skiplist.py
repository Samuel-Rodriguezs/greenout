import random
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from gr_skiplist import SkipList


class TestSkipList(unittest.TestCase):
    def test_vazia(self):
        s = SkipList(semente=1)
        self.assertEqual(len(s), 0)
        self.assertNotIn(1, s)
        self.assertFalse(s.remover(1))
        self.assertIsNone(s.menor_maior_igual(0))
        self.assertEqual(list(s), [])

    def test_inserir_ordenado_e_duplicata(self):
        s = SkipList(semente=1)
        for v in (5, 1, 9, 3, 5):
            s.inserir(v)
        self.assertEqual(list(s), [1, 3, 5, 9])
        self.assertEqual(len(s), 4)
        self.assertFalse(s.inserir(3))

    def test_remover(self):
        s = SkipList(semente=2)
        for v in range(20):
            s.inserir(v)
        for v in range(0, 20, 2):
            self.assertTrue(s.remover(v))
        self.assertEqual(list(s), list(range(1, 20, 2)))
        self.assertNotIn(4, s)
        self.assertIn(7, s)

    def test_menor_maior_igual(self):
        s = SkipList(semente=3)
        for v in (10, 20, 30):
            s.inserir(v)
        self.assertEqual(s.menor_maior_igual(15), 20)
        self.assertEqual(s.menor_maior_igual(30), 30)
        self.assertIsNone(s.menor_maior_igual(31))

    def test_aleatorio_contra_set(self):
        rnd = random.Random(7)
        s, ref = SkipList(semente=4), set()
        for _ in range(2000):
            v = rnd.randrange(200)
            if rnd.random() < 0.6:
                self.assertEqual(s.inserir(v), v not in ref)
                ref.add(v)
            else:
                self.assertEqual(s.remover(v), v in ref)
                ref.discard(v)
        self.assertEqual(list(s), sorted(ref))
        self.assertEqual(len(s), len(ref))

    def test_parametros_invalidos(self):
        with self.assertRaises(ValueError):
            SkipList(nivel_max=0)
        with self.assertRaises(ValueError):
            SkipList(p=1.0)


if __name__ == "__main__":
    unittest.main()
