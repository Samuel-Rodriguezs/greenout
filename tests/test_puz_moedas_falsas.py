import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from puz_moedas_falsas import (achar_diferente_12, achar_mais_leve,
                               balanca_para, pesagens_minimas_leve_conhecida,
                               pesagens_necessarias_desconhecida)


class TestMoedasFalsas(unittest.TestCase):
    def test_mais_leve_todas_posicoes(self):
        for n in (1, 2, 3, 8, 9, 10, 27, 28):
            for falsa in range(n):
                pesos = [10] * n
                pesos[falsa] = 9
                pesar, usos = balanca_para(pesos)
                self.assertEqual(achar_mais_leve(n, pesar), falsa)
                self.assertLessEqual(len(usos), pesagens_minimas_leve_conhecida(n))

    def test_limites_de_pesagens(self):
        self.assertEqual([pesagens_minimas_leve_conhecida(n) for n in (1, 2, 3, 4, 9, 10, 27)],
                         [0, 1, 1, 2, 2, 3, 3])

    def test_doze_moedas_todas_as_possibilidades(self):
        for falsa in range(12):
            for peso, tipo in ((9, "leve"), (11, "pesada")):
                pesos = [10] * 12
                pesos[falsa] = peso
                pesar, usos = balanca_para(pesos)
                self.assertEqual(achar_diferente_12(pesar), (falsa, tipo))
                self.assertLessEqual(len(usos), 3)

    def test_limite_de_informacao(self):
        self.assertEqual(pesagens_necessarias_desconhecida(12), 3)
        self.assertEqual(pesagens_necessarias_desconhecida(13), 4)
        self.assertEqual(pesagens_necessarias_desconhecida(3), 2)
        self.assertIsNone(pesagens_necessarias_desconhecida(2))

    def test_pratos_desiguais(self):
        pesar, _ = balanca_para([1, 1, 1])
        with self.assertRaises(ValueError):
            pesar([0], [1, 2])

    def test_n_invalido(self):
        with self.assertRaises(ValueError):
            pesagens_minimas_leve_conhecida(0)


if __name__ == "__main__":
    unittest.main()
