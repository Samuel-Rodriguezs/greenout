import random
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from gr_avl import ArvoreAVL


class TestAVL(unittest.TestCase):
    def test_vazia(self):
        a = ArvoreAVL()
        self.assertEqual(len(a), 0)
        self.assertEqual(a.altura(), 0)
        self.assertNotIn(1, a)
        self.assertFalse(a.remover(1))

    def test_sequencial_mantem_altura_log(self):
        a = ArvoreAVL()
        for i in range(1024):
            a.inserir(i)
        self.assertLessEqual(a.altura(), 11)
        self.assertTrue(a.balanceada())
        self.assertEqual(list(a), list(range(1024)))

    def test_duplicata(self):
        a = ArvoreAVL()
        self.assertTrue(a.inserir(5))
        self.assertFalse(a.inserir(5))
        self.assertEqual(len(a), 1)

    def test_rotacoes_duplas(self):
        a = ArvoreAVL()
        for c in (30, 10, 20):
            a.inserir(c)
        self.assertEqual(a.raiz.chave, 20)
        b = ArvoreAVL()
        for c in (10, 30, 20):
            b.inserir(c)
        self.assertEqual(b.raiz.chave, 20)

    def test_remocao_aleatoria(self):
        rnd = random.Random(42)
        valores = rnd.sample(range(1000), 300)
        a = ArvoreAVL()
        for v in valores:
            a.inserir(v)
        rnd.shuffle(valores)
        restantes = set(valores)
        for v in valores[:200]:
            self.assertTrue(a.remover(v))
            restantes.discard(v)
            self.assertTrue(a.balanceada())
        self.assertEqual(list(a), sorted(restantes))
        self.assertEqual(len(a), 100)
        self.assertFalse(a.remover(-1))


if __name__ == "__main__":
    unittest.main()
