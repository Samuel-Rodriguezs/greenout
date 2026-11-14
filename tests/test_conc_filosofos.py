import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from conc_filosofos import Mesa


class TestFilosofos(unittest.TestCase):
    def test_sem_deadlock_todos_comem(self):
        mesa = Mesa(5)
        self.assertTrue(mesa.jantar(100, timeout=3))
        self.assertEqual(mesa.refeicoes, [100] * 5)

    def test_vizinhos_nunca_comem_juntos(self):
        mesa = Mesa(5)
        mesa.jantar(100, timeout=3)
        self.assertEqual(mesa.violacoes, 0)

    def test_ordem_dos_garfos(self):
        mesa = Mesa(5)
        self.assertEqual(mesa.garfos_de(0), (0, 1))
        self.assertEqual(mesa.garfos_de(4), (0, 4))  # o último pega o menor primeiro

    def test_dois_filosofos(self):
        mesa = Mesa(2)
        self.assertTrue(mesa.jantar(50, timeout=3))
        self.assertEqual(sum(mesa.refeicoes), 100)

    def test_minimo(self):
        with self.assertRaises(ValueError):
            Mesa(1)


if __name__ == "__main__":
    unittest.main()
