import random
import sys
import unittest
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

import gen_nascimento as g

REF = date(2024, 2, 29)


class TestGenNascimento(unittest.TestCase):
    def test_idade_em(self):
        self.assertEqual(g.idade_em(date(2000, 3, 1), date(2024, 2, 29)), 23)
        self.assertEqual(g.idade_em(date(2000, 2, 29), date(2024, 2, 29)), 24)
        self.assertEqual(g.idade_em(date(2024, 2, 29), date(2024, 2, 29)), 0)

    def test_faixa_respeitada(self):
        rng = random.Random(1)
        for ref in (REF, date(2025, 6, 15), date(2023, 1, 1)):
            for nome, (lo, hi) in g.FAIXAS.items():
                for _ in range(200):
                    n = g.gerar_por_faixa(rng, ref, nome)
                    self.assertLessEqual(n, ref)
                    self.assertTrue(lo <= g.idade_em(n, ref) <= hi, (nome, n, ref))

    def test_extremos_alcancados(self):
        rng = random.Random(2)
        idades = {g.idade_em(g.gerar_nascimento(rng, REF, 18, 20), REF) for _ in range(2000)}
        self.assertEqual(idades, {18, 19, 20})

    def test_faixa_invalida(self):
        with self.assertRaises(ValueError):
            g.gerar_nascimento(random.Random(0), REF, 30, 20)
        with self.assertRaises(ValueError):
            g.gerar_por_faixa(random.Random(0), REF, "marciano")

    def test_populacao_determinismo_e_pesos(self):
        a = g.gerar_populacao(random.Random(3), REF, 500)
        self.assertEqual(a, g.gerar_populacao(random.Random(3), REF, 500))
        so_idosos = g.gerar_populacao(random.Random(3), REF, 30, {"idoso": 1})
        self.assertTrue(all(f == "idoso" for f, _ in so_idosos))
        adultos = sum(1 for f, _ in a if f == "adulto")
        criancas = sum(1 for f, _ in a if f == "crianca")
        self.assertGreater(adultos, criancas)


if __name__ == "__main__":
    unittest.main()
