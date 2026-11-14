import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from puz_kakuro import combinacoes_soma, contar_solucoes, resolver, sequencias


class TestKakuro(unittest.TestCase):
    def test_combinacoes(self):
        self.assertEqual(combinacoes_soma(4, 2), [(1, 3)])
        self.assertEqual(combinacoes_soma(23, 3), [(6, 8, 9)])
        self.assertEqual(combinacoes_soma(45, 9), [tuple(range(1, 10))])
        self.assertEqual(combinacoes_soma(3, 3), [])
        self.assertEqual(combinacoes_soma(10, 2), [(1, 9), (2, 8), (3, 7), (4, 6)])

    def test_sequencias(self):
        seqs = sequencias(["#..", "...", "..#"])
        self.assertEqual(set(seqs), {("H", (0, 1)), ("H", (1, 0)), ("H", (2, 0)),
                                     ("V", (0, 1)), ("V", (1, 0)), ("V", (0, 2))})
        self.assertEqual(seqs[("H", (1, 0))], [(1, 0), (1, 1), (1, 2)])

    def test_celula_solta_nao_forma_sequencia(self):
        self.assertEqual(sequencias([".#.", "###", ".#."]), {})

    def test_resolver_2x2(self):
        molde = ["..", ".."]
        pistas = [("H", (0, 0), 3), ("H", (1, 0), 7), ("V", (0, 0), 4), ("V", (0, 1), 6)]
        self.assertEqual(resolver(molde, pistas), [[1, 2], [3, 4]])
        self.assertEqual(contar_solucoes(molde, pistas), 1)

    def test_forma_irregular_confere_somas(self):
        molde = ["#..", "...", "..#"]
        pistas = [("H", (0, 1), 3), ("H", (1, 0), 8), ("H", (2, 0), 3),
                  ("V", (0, 1), 6), ("V", (1, 0), 5), ("V", (0, 2), 3)]
        sol = resolver(molde, pistas)
        self.assertIsNotNone(sol)
        seqs = sequencias(molde)
        somas = {(d, p): s for d, p, s in pistas}
        for chave, cels in seqs.items():
            valores = [sol[r][c] for r, c in cels]
            self.assertEqual(sum(valores), somas[chave])
            self.assertEqual(len(set(valores)), len(valores))
            self.assertTrue(all(1 <= v <= 9 for v in valores))
        self.assertEqual(sol[0][0], 0)  # célula preta fica 0

    def test_sem_solucao(self):
        pistas = [("H", (0, 0), 3), ("H", (1, 0), 3), ("V", (0, 0), 4), ("V", (0, 1), 2)]
        self.assertIsNone(resolver(["..", ".."], pistas))
        self.assertEqual(contar_solucoes(["..", ".."], pistas), 0)

    def test_soma_impossivel(self):
        pistas = [("H", (0, 0), 20), ("H", (1, 0), 3), ("V", (0, 0), 4), ("V", (0, 1), 6)]
        self.assertIsNone(resolver(["..", ".."], pistas))

    def test_ambiguo(self):
        pistas = [("H", (0, 0), 4), ("H", (1, 0), 4), ("V", (0, 0), 4), ("V", (0, 1), 4)]
        self.assertEqual(contar_solucoes(["..", ".."], pistas), 2)

    def test_pista_faltando(self):
        with self.assertRaises(ValueError):
            resolver(["..", ".."], [("H", (0, 0), 3)])

    def test_pista_inexistente(self):
        pistas = [("H", (0, 0), 3), ("H", (1, 0), 7), ("V", (0, 0), 4),
                  ("V", (0, 1), 6), ("H", (0, 1), 2)]
        with self.assertRaises(ValueError):
            resolver(["..", ".."], pistas)


if __name__ == "__main__":
    unittest.main()
