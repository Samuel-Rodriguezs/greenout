import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from puz_hashi import arestas_candidatas, ler_ilhas, resolver, verificar


class TestHashi(unittest.TestCase):
    def test_leitura(self):
        self.assertEqual(ler_ilhas(["2.1", "..."]), {(0, 0): 2, (0, 2): 1})
        with self.assertRaises(ValueError):
            ler_ilhas(["2x1"])

    def test_dois_pontos(self):
        ilhas = ler_ilhas(["2.2"])
        self.assertEqual(resolver(ilhas), {((0, 0), (0, 2)): 2})

    def test_uma_ponte(self):
        ilhas = ler_ilhas(["1.1"])
        self.assertEqual(resolver(ilhas), {((0, 0), (0, 2)): 1})

    def test_arestas_ignoram_ilha_atras_de_outra(self):
        ilhas = ler_ilhas(["1.2.1"])
        self.assertEqual(arestas_candidatas(ilhas), [((0, 0), (0, 2)), ((0, 2), (0, 4))])

    def test_quadrado(self):
        diagrama = ["2.2", "...", "2.2"]
        ilhas = ler_ilhas(diagrama)
        sol = resolver(ilhas)
        self.assertIsNotNone(sol)
        self.assertTrue(verificar(ilhas, sol))
        self.assertEqual(sum(sol.values()), 4)

    def test_anel_tem_duas_solucoes_validas(self):
        ilhas = ler_ilhas(["3.3", "...", "3.3"])
        sol = resolver(ilhas)
        self.assertIsNotNone(sol)
        self.assertTrue(verificar(ilhas, sol))
        self.assertEqual(sum(sol.values()), 6)

    def test_puzzle_2x3_construido_de_solucao_conhecida(self):
        ilhas = ler_ilhas(["2.4.3", ".....", "2.4.3"])
        sol = resolver(ilhas)
        self.assertIsNotNone(sol)
        self.assertTrue(verificar(ilhas, sol))
        self.assertEqual(sum(sol.values()) * 2, sum(ilhas.values()))

    def test_cruzamento_proibido(self):
        # a única forma de saturar as ilhas exigiria pontes que se cruzam
        ilhas = ler_ilhas([".1.", "1.1", ".1."])
        self.assertIsNone(resolver(ilhas))

    def test_verificar_rejeita_graus_errados_e_cruzamento(self):
        ilhas = ler_ilhas(["2.2"])
        self.assertFalse(verificar(ilhas, {((0, 0), (0, 2)): 1}))
        cruz = ler_ilhas([".1.", "1.1", ".1."])
        pontes = {((0, 1), (2, 1)): 1, ((1, 0), (1, 2)): 1}
        self.assertFalse(verificar(cruz, pontes))

    def test_soma_impar_sem_solucao(self):
        self.assertIsNone(resolver(ler_ilhas(["1.2"])))

    def test_desconexo_sem_solucao(self):
        # dois pares isolados: graus fecham, mas o grafo fica desconexo
        ilhas = ler_ilhas(["1.1", "...", "1.1"])
        self.assertIsNone(resolver(ilhas))

    def test_demais_pontes_sem_solucao(self):
        self.assertIsNone(resolver(ler_ilhas(["3.3"])))

    def test_vazio(self):
        self.assertEqual(resolver({}), {})


if __name__ == "__main__":
    unittest.main()
