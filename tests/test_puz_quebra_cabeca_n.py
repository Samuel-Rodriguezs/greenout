import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from puz_quebra_cabeca_n import (aplicar, embaralhar, estado_objetivo,
                                 manhattan, resolver, resolvivel)


class TestQuebraCabecaN(unittest.TestCase):
    def test_objetivo_ja_resolvido(self):
        self.assertEqual(resolver(estado_objetivo(3), 3), [])

    def test_manhattan(self):
        self.assertEqual(manhattan(estado_objetivo(3), 3), 0)
        self.assertEqual(manhattan((1, 2, 3, 4, 5, 6, 7, 0, 8), 3), 1)

    def test_um_movimento(self):
        self.assertEqual(resolver((1, 2, 3, 4, 5, 6, 7, 0, 8), 3), ["D"])

    def test_conhecido_otimo(self):
        # instância clássica com solução ótima de 8 movimentos
        estado = (1, 2, 3, 4, 5, 6, 0, 7, 8)
        sol = resolver(estado, 3)
        self.assertEqual(len(sol), 2)
        self.assertEqual(aplicar(estado, 3, sol), estado_objetivo(3))

    def test_embaralhado_8(self):
        estado = embaralhar(3, 40, seed=1)
        sol = resolver(estado, 3)
        self.assertEqual(aplicar(estado, 3, sol), estado_objetivo(3))

    def test_embaralhado_15(self):
        estado = embaralhar(4, 14, seed=3)
        sol = resolver(estado, 4)
        self.assertLessEqual(len(sol), 14)
        self.assertEqual(aplicar(estado, 4, sol), estado_objetivo(4))

    def test_insolucionavel(self):
        estado = (2, 1, 3, 4, 5, 6, 7, 8, 0)
        self.assertFalse(resolvivel(estado, 3))
        self.assertIsNone(resolver(estado, 3))
        self.assertFalse(resolvivel((1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 15, 14, 0), 4))

    def test_invalido(self):
        with self.assertRaises(ValueError):
            resolver((1, 2, 3), 3)


if __name__ == "__main__":
    unittest.main()
