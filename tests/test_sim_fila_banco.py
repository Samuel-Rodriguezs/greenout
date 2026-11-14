import random
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from sim_fila_banco import simular


class TestFilaBanco(unittest.TestCase):
    def test_determinismo(self):
        a = simular(480, 2, 0.4, 4, random.Random(1))
        b = simular(480, 2, 0.4, 4, random.Random(1))
        self.assertEqual(a, b)

    def test_sem_chegadas(self):
        r = simular(100, 1, 0.0, 3, random.Random(1))
        self.assertEqual((r.atendidos, r.espera_media, r.fila_maxima, r.ocupacao), (0, 0.0, 0, 0.0))

    def test_mais_caixas_reduz_espera(self):
        um = simular(2000, 1, 0.3, 3, random.Random(5))
        tres = simular(2000, 3, 0.3, 3, random.Random(5))
        self.assertLess(tres.espera_media, um.espera_media)
        self.assertLessEqual(tres.fila_maxima, um.fila_maxima)

    def test_sistema_sobrecarregado(self):
        r = simular(500, 1, 0.9, 5, random.Random(2))
        self.assertGreater(r.fila_maxima, 50)
        self.assertGreater(r.ocupacao, 0.95)

    def test_atendimento_instantaneo_sem_espera(self):
        r = simular(300, 5, 0.2, 1, random.Random(3))
        self.assertEqual(r.espera_maxima, 0)
        self.assertGreater(r.atendidos, 0)

    def test_validacoes(self):
        with self.assertRaises(ValueError):
            simular(10, 0, 0.5, 2, random.Random(1))
        with self.assertRaises(ValueError):
            simular(10, 1, 1.5, 2, random.Random(1))
        with self.assertRaises(ValueError):
            simular(10, 1, 0.5, 0, random.Random(1))


if __name__ == "__main__":
    unittest.main()
