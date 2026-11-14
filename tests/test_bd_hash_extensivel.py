import random
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from bd_hash_extensivel import HashExtensivel


class TestHashExtensivel(unittest.TestCase):
    def test_capacidade_invalida(self):
        with self.assertRaises(ValueError):
            HashExtensivel(0)

    def test_vazio(self):
        h = HashExtensivel()
        self.assertIsNone(h.buscar("x"))
        self.assertFalse(h.remover("x"))
        self.assertEqual(h.profundidade, 0)

    def test_inserir_buscar_com_crescimento(self):
        h = HashExtensivel(2)
        for i in range(500):
            h.inserir(i, i * 3)
        self.assertEqual(len(h), 500)
        self.assertGreater(h.profundidade, 3)
        for i in range(500):
            self.assertEqual(h.buscar(i), i * 3)
        self.assertEqual(sorted(h.chaves()), list(range(500)))
        self.assertLessEqual(h.baldes_distintos(), len(h.diretorio))

    def test_atualiza(self):
        h = HashExtensivel()
        h.inserir("a", 1)
        h.inserir("a", 2)
        self.assertEqual(len(h), 1)
        self.assertEqual(h.buscar("a"), 2)
        self.assertIn("a", h)

    def test_invariante_profundidade_local(self):
        h = HashExtensivel(3)
        for i in range(300):
            h.inserir(f"k{i}", i)
        for i, b in enumerate(h.diretorio):
            self.assertLessEqual(b.profundidade, h.profundidade)
            for k in b.itens:
                self.assertIs(h.diretorio[h._indice(k)], b)

    def test_remocao_encolhe_diretorio(self):
        h = HashExtensivel(2)
        for i in range(200):
            h.inserir(i)
        cheio = h.profundidade
        for i in range(200):
            self.assertTrue(h.remover(i))
        self.assertEqual(len(h), 0)
        self.assertLess(h.profundidade, cheio)
        self.assertEqual(h.profundidade, 0)
        h.inserir(1, "x")
        self.assertEqual(h.buscar(1), "x")

    def test_aleatorio_contra_dict(self):
        rnd = random.Random(5)
        h, ref = HashExtensivel(3), {}
        for _ in range(3000):
            k = rnd.randrange(400)
            if rnd.random() < 0.6:
                h.inserir(k, k + 1)
                ref[k] = k + 1
            else:
                self.assertEqual(h.remover(k), ref.pop(k, None) is not None)
        self.assertEqual(len(h), len(ref))
        for k in range(400):
            self.assertEqual(h.buscar(k), ref.get(k))


if __name__ == "__main__":
    unittest.main()
