import random
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from bd_bmais import BMais


class TestBMais(unittest.TestCase):
    def test_ordem_invalida(self):
        with self.assertRaises(ValueError):
            BMais(2)

    def test_vazia(self):
        b = BMais()
        self.assertIsNone(b.buscar(1))
        self.assertEqual(list(b.intervalo()), [])
        self.assertFalse(b.remover(1))

    def test_inserir_e_varrer_em_ordem(self):
        rnd = random.Random(3)
        chaves = list(range(200))
        rnd.shuffle(chaves)
        b = BMais(4)
        for k in chaves:
            b.inserir(k, k * k)
        self.assertEqual(len(b), 200)
        self.assertEqual([k for k, _ in b.itens()], list(range(200)))
        self.assertEqual(b.buscar(12), 144)
        self.assertGreater(b.altura(), 2)

    def test_intervalo(self):
        b = BMais(5)
        for k in range(0, 100, 2):
            b.inserir(k, k)
        self.assertEqual([k for k, _ in b.intervalo(10, 20)], [10, 12, 14, 16, 18, 20])
        self.assertEqual([k for k, _ in b.intervalo(10, 20, incluir_hi=False)], [10, 12, 14, 16, 18])
        self.assertEqual([k for k, _ in b.intervalo(11, 15)], [12, 14])
        self.assertEqual([k for k, _ in b.intervalo(95, None)], [96, 98])
        self.assertEqual([k for k, _ in b.intervalo(None, 4)], [0, 2, 4])
        self.assertEqual(list(b.intervalo(200, 300)), [])
        self.assertEqual(list(b.intervalo(21, 21)), [])

    def test_atualiza_duplicada(self):
        b = BMais()
        b.inserir(1, "a")
        b.inserir(1, "b")
        self.assertEqual(len(b), 1)
        self.assertEqual(b.buscar(1), "b")

    def test_remocao_aleatoria_consistente(self):
        rnd = random.Random(11)
        b = BMais(4)
        ref = {}
        for _ in range(1500):
            k = rnd.randrange(150)
            if rnd.random() < 0.55:
                b.inserir(k, k)
                ref[k] = k
            else:
                self.assertEqual(b.remover(k), k in ref)
                ref.pop(k, None)
        self.assertEqual(len(b), len(ref))
        self.assertEqual(list(b.itens()), sorted(ref.items()))
        for k in range(150):
            self.assertEqual(b.buscar(k), ref.get(k))
        self.assertEqual([k for k, _ in b.intervalo(30, 60)], [k for k in sorted(ref) if 30 <= k <= 60])

    def test_remover_tudo(self):
        b = BMais(3)
        for k in range(50):
            b.inserir(k)
        for k in range(50):
            self.assertTrue(b.remover(k))
        self.assertEqual(len(b), 0)
        self.assertEqual(list(b.itens()), [])
        b.inserir(7, "x")
        self.assertEqual(b.buscar(7), "x")


if __name__ == "__main__":
    unittest.main()
