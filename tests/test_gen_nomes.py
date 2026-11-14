import random
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

import gen_nomes as g


class TestGenNomes(unittest.TestCase):
    def test_determinismo(self):
        a = g.gerar_lote(random.Random(7), 30)
        b = g.gerar_lote(random.Random(7), 30)
        self.assertEqual(a, b)
        self.assertNotEqual(a, g.gerar_lote(random.Random(8), 30))

    def test_genero(self):
        rng = random.Random(1)
        for _ in range(50):
            self.assertIn(g.gerar_nome(rng, "M"), g.NOMES_MASCULINOS)
            self.assertIn(g.gerar_nome(rng, "F"), g.NOMES_FEMININOS)
        with self.assertRaises(ValueError):
            g.gerar_nome(rng, "X")

    def test_sobrenomes_distintos_e_validos(self):
        rng = random.Random(3)
        for _ in range(100):
            partes = g.gerar_nome_completo(rng, n_sobrenomes=3).split()
            sobres = [p for p in partes[1:] if p not in g.PARTICULAS]
            self.assertEqual(len(sobres), 3)
            self.assertEqual(len(set(sobres)), 3)
            self.assertTrue(all(s in g.SOBRENOMES for s in sobres))

    def test_n_sobrenomes_invalido(self):
        with self.assertRaises(ValueError):
            g.gerar_nome_completo(random.Random(0), n_sobrenomes=0)

    def test_particula_aparece_no_lote(self):
        lote = g.gerar_lote(random.Random(5), 200)
        self.assertTrue(any(set(n.split()) & g.PARTICULAS for n in lote))


if __name__ == "__main__":
    unittest.main()
