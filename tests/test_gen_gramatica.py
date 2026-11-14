import random
import re
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

import gen_gramatica as g


class TestGenGramatica(unittest.TestCase):
    def test_determinismo(self):
        a = g.gerar_lote(1, g.GRAMATICA_SAUDACOES, 30)
        self.assertEqual(a, g.gerar_lote(1, g.GRAMATICA_SAUDACOES, 30))
        self.assertNotEqual(a, g.gerar_lote(2, g.GRAMATICA_SAUDACOES, 30))

    def test_sem_marcadores_residuais_e_forma(self):
        for s in g.gerar_lote(3, g.GRAMATICA_SAUDACOES, 200):
            self.assertNotRegex(s, r"[{}]")
            self.assertRegex(s, r"^(Olá|Bom dia|Boa tarde|Oi), ")
            self.assertTrue(s.endswith((".", "?")))

    def test_cobre_todas_as_alternativas_de_saudacao(self):
        vistos = {s.split(",")[0] for s in g.gerar_lote(4, g.GRAMATICA_SAUDACOES, 300)}
        self.assertEqual(vistos, {"Olá", "Bom dia", "Boa tarde", "Oi"})

    def test_recursao_limitada_pela_profundidade(self):
        gram = {"inicio": ["({inicio})", "x"]}
        g.validar(gram, "inicio")
        for seed in range(50):
            s = g.expandir(random.Random(seed), gram, profundidade_max=5)
            self.assertEqual(s.strip("()"), "x")
            self.assertLessEqual(s.count("("), 5)

    def test_profundidade_limita_tamanho_em_gramatica_binaria(self):
        gram = {"inicio": ["{n}", "({inicio}+{inicio})"], "n": ["1"]}
        for seed in range(30):
            s = g.expandir(random.Random(seed), gram, profundidade_max=3)
            self.assertLessEqual(s.count("1"), 2 ** 4)

    def test_validacao(self):
        with self.assertRaises(ValueError):
            g.validar({"inicio": ["{faltando}"]}, "inicio")
        with self.assertRaises(ValueError):
            g.validar({"inicio": ["{inicio}"]}, "inicio")  # sem derivação finita
        with self.assertRaises(ValueError):
            g.validar({"inicio": []}, "inicio")
        with self.assertRaises(ValueError):
            g.validar({"a": ["x"]}, "inicio")

    def test_preencher(self):
        self.assertEqual(g.preencher("Olá, {nome}! {nome}.", {"nome": "Ana"}), "Olá, Ana! Ana.")
        with self.assertRaises(KeyError):
            g.preencher("{x}", {})

    def test_gramatica_aritmetica(self):
        gram = {"inicio": ["{n}", "({inicio}{op}{inicio})"], "n": ["1", "2", "3"], "op": ["+", "*"]}
        rng = random.Random(5)
        for _ in range(100):
            s = g.expandir(rng, gram, profundidade_max=4)
            self.assertIsNotNone(re.fullmatch(r"[0-9()+*]+", s))
            self.assertEqual(s.count("("), s.count(")"))
            eval(s)  # expressão sintaticamente válida


if __name__ == "__main__":
    unittest.main()
