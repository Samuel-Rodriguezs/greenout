import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from puz_missionarios import resolver, valido


def simular(n, passos):
    m, c, barco = n, n, True
    for dm, dc in passos:
        s = -1 if barco else 1
        m, c, barco = m + s * dm, c + s * dc, not barco
        assert valido(m, c, n)
    return m, c, barco


class TestMissionarios(unittest.TestCase):
    def test_classico_3_3_barco_2(self):
        sol = resolver(3, 2)
        self.assertEqual(len(sol), 11)
        self.assertEqual(simular(3, sol), (0, 0, False))

    def test_dois_cada_barco_2(self):
        self.assertEqual(len(resolver(2, 2)), 5)

    def test_quatro_cada_barco_2_impossivel(self):
        self.assertIsNone(resolver(4, 2))
        self.assertIsNone(resolver(5, 2))

    def test_barco_3_resolve_quatro(self):
        sol = resolver(4, 3)
        self.assertIsNotNone(sol)
        self.assertEqual(simular(4, sol), (0, 0, False))

    def test_zero_pessoas(self):
        self.assertEqual(resolver(0, 2), [])

    def test_validade(self):
        self.assertFalse(valido(1, 2, 3))
        self.assertTrue(valido(0, 3, 3))
        self.assertFalse(valido(4, 0, 3))

    def test_parametros_invalidos(self):
        with self.assertRaises(ValueError):
            resolver(3, 0)


if __name__ == "__main__":
    unittest.main()
