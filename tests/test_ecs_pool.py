import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from ecs_pool import PoolObjetos


class TestPool(unittest.TestCase):
    def test_reutiliza_objeto(self):
        p = PoolObjetos(list)
        a = p.adquirir()
        p.liberar(a)
        self.assertIs(p.adquirir(), a)
        self.assertEqual(p.criados, 1)

    def test_resetar_ao_liberar(self):
        p = PoolObjetos(list, resetar=lambda l: l.clear())
        a = p.adquirir()
        a.append(1)
        p.liberar(a)
        self.assertEqual(a, [])

    def test_capacidade(self):
        p = PoolObjetos(dict, capacidade=2)
        a, b = p.adquirir(), p.adquirir()
        with self.assertRaises(RuntimeError):
            p.adquirir()
        p.liberar(a)
        self.assertIs(p.adquirir(), a)
        self.assertEqual((p.em_uso, p.livres), (2, 0))

    def test_liberar_duas_vezes(self):
        p = PoolObjetos(list)
        a = p.adquirir()
        p.liberar(a)
        with self.assertRaises(ValueError):
            p.liberar(a)
        with self.assertRaises(ValueError):
            p.liberar([])

    def test_capacidade_invalida(self):
        with self.assertRaises(ValueError):
            PoolObjetos(list, capacidade=0)


if __name__ == "__main__":
    unittest.main()
