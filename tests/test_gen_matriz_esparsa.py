import random
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

import gen_matriz_esparsa as g


class TestGenMatrizEsparsa(unittest.TestCase):
    def test_coo_contagem_unicidade_limites(self):
        coo = g.gerar_coo(random.Random(1), 20, 30, 0.1)
        self.assertEqual(len(coo), 60)
        pos = [(i, j) for i, j, _ in coo]
        self.assertEqual(len(set(pos)), 60)
        self.assertEqual(pos, sorted(pos))
        self.assertTrue(all(0 <= i < 20 and 0 <= j < 30 for i, j in pos))
        self.assertTrue(all(v != 0 for _, _, v in coo))

    def test_densidades_extremas(self):
        self.assertEqual(g.gerar_coo(random.Random(1), 4, 4, 0.0), [])
        self.assertEqual(len(g.gerar_coo(random.Random(1), 4, 4, 1.0)), 16)

    def test_determinismo(self):
        self.assertEqual(g.gerar_csr(random.Random(2), 15, 15, 0.2), g.gerar_csr(random.Random(2), 15, 15, 0.2))

    def test_csr_estrutura(self):
        m = g.gerar_csr(random.Random(3), 12, 9, 0.25)
        self.assertEqual(len(m.ponteiros_linha), 13)
        self.assertEqual(m.ponteiros_linha[0], 0)
        self.assertEqual(m.ponteiros_linha[-1], m.nnz)
        self.assertTrue(all(a <= b for a, b in zip(m.ponteiros_linha, m.ponteiros_linha[1:])))
        for i in range(12):
            cols = m.indices_coluna[m.ponteiros_linha[i]:m.ponteiros_linha[i + 1]]
            self.assertEqual(list(cols), sorted(set(cols)))

    def test_multiplicacao_igual_a_densa(self):
        rng = random.Random(4)
        m = g.gerar_csr(rng, 25, 18, 0.15)
        x = [rng.uniform(-1, 1) for _ in range(18)]
        densa = m.para_densa()
        esperado = [sum(a * b for a, b in zip(linha, x)) for linha in densa]
        for a, b in zip(m.multiplicar(x), esperado):
            self.assertAlmostEqual(a, b)

    def test_dimensao_invalida(self):
        m = g.gerar_csr(random.Random(5), 3, 3, 0.5)
        with self.assertRaises(ValueError):
            m.multiplicar([1.0])
        with self.assertRaises(ValueError):
            g.gerar_coo(random.Random(0), 0, 3, 0.5)
        with self.assertRaises(ValueError):
            g.gerar_coo(random.Random(0), 3, 3, 2.0)
        with self.assertRaises(ValueError):
            g.coo_para_csr(2, 2, [(5, 0, 1.0)])

    def test_coo_csr_roundtrip(self):
        coo = g.gerar_coo(random.Random(6), 10, 10, 0.3)
        densa = g.coo_para_csr(10, 10, coo).para_densa()
        for i, j, v in coo:
            self.assertEqual(densa[i][j], v)
        self.assertEqual(sum(1 for r in densa for x in r if x), len(coo))


if __name__ == "__main__":
    unittest.main()
