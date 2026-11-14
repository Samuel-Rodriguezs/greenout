import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from puz_cobertura_exata import (PENTOMINOS, cobertura_exata,
                                 contar_ladrilhamentos, ladrilhar, orientacoes,
                                 retangulo)


class TestCoberturaExata(unittest.TestCase):
    def test_exemplo_de_knuth(self):
        universo = [1, 2, 3, 4, 5, 6, 7]
        subs = [{1, 4, 7}, {1, 4}, {4, 5, 7}, {3, 5, 6}, {2, 3, 6, 7}, {2, 7}]
        sols = [sorted(s) for s in cobertura_exata(universo, subs)]
        self.assertEqual(sols, [[1, 3, 5]])

    def test_sem_solucao(self):
        self.assertEqual(list(cobertura_exata([1, 2, 3], [{1, 2}, {2, 3}])), [])

    def test_varias_solucoes(self):
        sols = list(cobertura_exata([1, 2], [{1}, {2}, {1, 2}]))
        self.assertEqual(sorted(sorted(s) for s in sols), [[0, 1], [2]])

    def test_universo_vazio(self):
        self.assertEqual(list(cobertura_exata([], [])), [[]])

    def test_numero_de_orientacoes(self):
        esperado = {"F": 8, "I": 2, "L": 8, "N": 8, "P": 8, "T": 4,
                    "U": 4, "V": 4, "W": 4, "X": 1, "Y": 8, "Z": 4}
        for nome, forma in PENTOMINOS.items():
            self.assertEqual(len(orientacoes(forma)), esperado[nome], nome)

    def test_todas_as_pecas_tem_cinco_celulas(self):
        for forma in PENTOMINOS.values():
            self.assertEqual(len(set(forma)), 5)

    def test_i_em_linha(self):
        self.assertEqual(contar_ladrilhamentos(retangulo(1, 5), ["I"]), 1)
        self.assertEqual(contar_ladrilhamentos(retangulo(5, 1), ["I"]), 1)

    def test_x_nao_cabe_em_retangulo_1x5(self):
        self.assertEqual(contar_ladrilhamentos(retangulo(1, 5), ["X"]), 0)

    def test_tres_pecas_em_3x5(self):
        regiao = retangulo(3, 5)
        self.assertGreater(contar_ladrilhamentos(regiao, ["U", "V", "P"]), 0)
        tab = ladrilhar(regiao, ["U", "V", "P"])
        self.assertEqual(set(tab), regiao)
        self.assertEqual(sorted(set(tab.values())), ["P", "U", "V"])
        self.assertEqual(sum(1 for v in tab.values() if v == "U"), 5)

    def test_tamanho_incompativel(self):
        self.assertIsNone(ladrilhar(retangulo(2, 2), ["I"]))
        self.assertIsNone(ladrilhar(retangulo(1, 10), ["I", "I"]))  # peça repetida

    def test_doze_pecas_em_6x10(self):
        regiao = retangulo(6, 10)
        tab = ladrilhar(regiao, list(PENTOMINOS))
        self.assertEqual(set(tab), regiao)
        for nome in PENTOMINOS:
            self.assertEqual(sum(1 for v in tab.values() if v == nome), 5)


if __name__ == "__main__":
    unittest.main()
