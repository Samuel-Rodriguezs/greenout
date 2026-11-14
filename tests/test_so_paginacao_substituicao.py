import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from so_paginacao_substituicao import anomalia_belady, faltas_por_quadros, simular

SILBERSCHATZ = [7, 0, 1, 2, 0, 3, 0, 4, 2, 3, 0, 3, 2, 1, 2, 0, 1, 7, 0, 1]
BELADY = [1, 2, 3, 4, 1, 2, 5, 1, 2, 3, 4, 5]


class TestSubstituicao(unittest.TestCase):
    def test_fifo_livro(self):
        self.assertEqual(simular(SILBERSCHATZ, 3, "fifo").faltas, 15)

    def test_lru_livro(self):
        self.assertEqual(simular(SILBERSCHATZ, 3, "lru").faltas, 12)

    def test_otimo_livro(self):
        self.assertEqual(simular(SILBERSCHATZ, 3, "otimo").faltas, 9)

    def test_otimo_e_limite_inferior(self):
        otimo = simular(SILBERSCHATZ, 3, "otimo").faltas
        for pol in ("fifo", "lru", "clock", "lfu"):
            self.assertGreaterEqual(simular(SILBERSCHATZ, 3, pol).faltas, otimo)

    def test_estados_fifo_inicio(self):
        r = simular(SILBERSCHATZ, 3, "fifo")
        self.assertEqual(r.quadros[0], (7, None, None))
        self.assertEqual(r.quadros[2], (7, 0, 1))
        self.assertEqual(r.quadros[3], (2, 0, 1))  # 2 substitui o 7 (mais antigo)
        self.assertEqual(r.houve_falta[:5], (True, True, True, True, False))

    def test_clock_segunda_chance(self):
        r = simular([1, 2, 3, 1, 4, 2, 5], 3, "clock")
        self.assertEqual(r.faltas, 5)
        self.assertEqual(r.quadros[4], (4, 2, 3))
        self.assertEqual(r.quadros[-1], (4, 2, 5))

    def test_lfu_remove_menos_frequente(self):
        r = simular([1, 1, 2, 3], 2, "lfu")
        self.assertEqual(r.quadros[-1], (1, 3))

    def test_anomalia_de_belady_fifo(self):
        self.assertEqual(simular(BELADY, 3, "fifo").faltas, 9)
        self.assertEqual(simular(BELADY, 4, "fifo").faltas, 10)
        self.assertIn(((3, 9), (4, 10)), anomalia_belady(BELADY, "fifo", 6))

    def test_lru_e_otimo_nao_tem_anomalia(self):
        self.assertEqual(anomalia_belady(BELADY, "lru", 8), [])
        self.assertEqual(anomalia_belady(BELADY, "otimo", 8), [])

    def test_serie_e_taxa(self):
        serie = faltas_por_quadros(BELADY, "lru", 12)
        self.assertEqual(serie[-1], (12, 5))  # só faltas compulsórias (5 páginas)
        self.assertAlmostEqual(simular(BELADY, 3, "fifo").taxa_faltas, 9 / 12)

    def test_validacao(self):
        with self.assertRaises(ValueError):
            simular([1], 0, "fifo")
        with self.assertRaises(ValueError):
            simular([1], 1, "mru")


if __name__ == "__main__":
    unittest.main()
