import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from so_deadlock_grafo import GrafoAlocacao, detectar_matrizes

# Silberschatz: A=7, B=2, C=6
ALOC = [[0, 1, 0], [2, 0, 0], [3, 0, 3], [2, 1, 1], [0, 0, 2]]


class TestDeadlockMatrizes(unittest.TestCase):
    def test_sem_deadlock_no_livro(self):
        req = [[0, 0, 0], [2, 0, 2], [0, 0, 0], [1, 0, 0], [0, 0, 2]]
        self.assertEqual(detectar_matrizes([0, 0, 0], ALOC, req), [])

    def test_p2_pede_mais_um_c_e_causa_deadlock(self):
        req = [[0, 0, 0], [2, 0, 2], [0, 0, 1], [1, 0, 0], [0, 0, 2]]
        self.assertEqual(detectar_matrizes([0, 0, 0], ALOC, req), [1, 2, 3, 4])

    def test_recursos_disponiveis_desfazem_o_impasse(self):
        req = [[0, 0, 0], [2, 0, 2], [0, 0, 1], [1, 0, 0], [0, 0, 2]]
        self.assertEqual(detectar_matrizes([0, 0, 1], ALOC, req), [])


class TestGrafo(unittest.TestCase):
    def duas_travas(self) -> GrafoAlocacao:
        g = GrafoAlocacao()
        for p in ("P1", "P2"):
            g.processo(p)
        for r in ("R1", "R2"):
            g.recurso(r)
        g.alocar("P1", "R1")
        g.alocar("P2", "R2")
        g.requisitar("P1", "R2")
        g.requisitar("P2", "R1")
        return g

    def test_ciclo_e_deadlock_com_instancia_unica(self):
        g = self.duas_travas()
        self.assertEqual(g.ciclo(), ["P1", "R2", "P2", "R1"])
        self.assertEqual(g.deadlock(), ["P1", "P2"])

    def test_sem_ciclo_quando_um_recurso_esta_livre(self):
        g = GrafoAlocacao()
        g.processo("P1")
        g.recurso("R1")
        g.requisitar("P1", "R1")
        self.assertIsNone(g.ciclo())
        self.assertEqual(g.deadlock(), [])

    def test_ciclo_sem_deadlock_com_varias_instancias(self):
        g = GrafoAlocacao()
        for p in ("P1", "P2", "P3"):
            g.processo(p)
        g.recurso("R1", 2)
        g.recurso("R2", 1)
        g.alocar("P2", "R1")  # P2 roda livre e liberará R1
        g.alocar("P3", "R1")
        g.alocar("P1", "R2")
        g.requisitar("P1", "R1")
        g.requisitar("P3", "R2")
        self.assertIsNotNone(g.ciclo())  # P1 -> R1 -> P3 -> R2 -> P1
        self.assertEqual(g.deadlock(), [])

    def test_deadlock_em_tres_processos_com_um_inocente(self):
        g = GrafoAlocacao()
        for p in ("A", "B", "C", "D"):
            g.processo(p)
        for r in ("x", "y", "z"):
            g.recurso(r)
        g.alocar("A", "x")
        g.alocar("B", "y")
        g.alocar("C", "z")
        g.requisitar("A", "y")
        g.requisitar("B", "z")
        g.requisitar("C", "x")
        g.requisitar("D", "x")  # D só espera, não segura nada
        self.assertEqual(g.deadlock(), ["A", "B", "C"])

    def test_validacoes(self):
        g = GrafoAlocacao()
        g.processo("P")
        g.recurso("R", 1)
        with self.assertRaises(ValueError):
            g.processo("R")
        with self.assertRaises(ValueError):
            g.recurso("R")
        g.alocar("P", "R")
        with self.assertRaises(ValueError):
            g.alocar("P", "R")  # sem instância livre
        with self.assertRaises(ValueError):
            g.requisitar("Q", "R")


if __name__ == "__main__":
    unittest.main()
