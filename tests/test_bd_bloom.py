import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from bd_bloom import BloomFilter


class TestBloom(unittest.TestCase):
    def test_parametros_invalidos(self):
        with self.assertRaises(ValueError):
            BloomFilter(0, 1)
        with self.assertRaises(ValueError):
            BloomFilter.para(0)
        with self.assertRaises(ValueError):
            BloomFilter.para(10, 1.5)

    def test_vazio_nao_contem_nada(self):
        f = BloomFilter.para(100)
        self.assertNotIn("a", f)

    def test_sem_falsos_negativos(self):
        f = BloomFilter.para(1000, 0.01)
        for i in range(1000):
            f.adicionar(f"chave-{i}")
        self.assertTrue(all(f"chave-{i}" in f for i in range(1000)))

    def test_taxa_de_falsos_positivos_dentro_do_esperado(self):
        f = BloomFilter.para(2000, 0.01)
        for i in range(2000):
            f.adicionar(i)
        fps = sum(1 for i in range(10_000, 30_000) if i in f)
        self.assertLess(fps / 20_000, 0.03)
        self.assertLess(f.taxa_fp_estimada(), 0.02)

    def test_tipos_misturados_nao_colidem_por_repr(self):
        f = BloomFilter.para(100)
        f.adicionar(1)
        self.assertIn(1, f)
        # "1" tem repr diferente de 1 (aspas): é outro item
        self.assertEqual(f.n, 1)

    def test_uniao(self):
        a, b = BloomFilter(512, 3), BloomFilter(512, 3)
        a.adicionar("x")
        b.adicionar("y")
        u = a.uniao(b)
        self.assertIn("x", u)
        self.assertIn("y", u)
        with self.assertRaises(ValueError):
            a.uniao(BloomFilter(256, 3))

    def test_serializacao(self):
        f = BloomFilter.para(50)
        for i in range(50):
            f.adicionar(i)
        g = BloomFilter.de_bytes(f.para_bytes())
        self.assertTrue(all(i in g for i in range(50)))
        self.assertEqual(g.bits, f.bits)

    def test_serializacao_invalida(self):
        with self.assertRaises(ValueError):
            BloomFilter.de_bytes(b"\x01")
        bom = BloomFilter(64, 2).para_bytes()
        with self.assertRaises(ValueError):
            BloomFilter.de_bytes(bom[:-1])


if __name__ == "__main__":
    unittest.main()
