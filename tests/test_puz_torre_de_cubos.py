import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from puz_torre_de_cubos import (CLASSICO, mesmo_cubo, orientacoes, resolver,
                                verificar)


class TestTorreDeCubos(unittest.TestCase):
    def test_24_orientacoes_de_cubo_com_cores_distintas(self):
        cubo = ("1", "2", "3", "4", "5", "6")
        ors = orientacoes(cubo)
        self.assertEqual(len(ors), 24)
        for o in ors:
            # faces opostas continuam opostas: (topo,base), (frente,trás), (esq,dir)
            self.assertEqual(sorted(o), sorted(cubo))
        self.assertTrue(mesmo_cubo(cubo, ors[7]))

    def test_cores_repetidas_reduzem_orientacoes(self):
        self.assertEqual(len(orientacoes(("R",) * 6)), 1)

    def test_resolve_classico(self):
        torre = resolver(CLASSICO)
        self.assertIsNotNone(torre)
        self.assertTrue(verificar(torre))
        for original, usado in zip(CLASSICO, torre):
            self.assertTrue(mesmo_cubo(original, usado))

    def test_um_cubo(self):
        self.assertEqual(len(resolver([("R", "G", "B", "W", "Y", "K")])), 1)

    def test_vazio(self):
        self.assertEqual(resolver([]), [])

    def test_sem_solucao_cores_insuficientes(self):
        self.assertIsNone(resolver([("R",) * 6, ("G",) * 6, ("R",) * 6]))

    def test_sem_solucao_cubos_iguais_monocromaticos(self):
        self.assertIsNone(resolver([("R",) * 6, ("R",) * 6]))

    def test_verificar_rejeita(self):
        self.assertFalse(verificar(CLASSICO))  # sem orientar, os lados repetem cores


if __name__ == "__main__":
    unittest.main()
