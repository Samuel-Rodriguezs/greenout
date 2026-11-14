import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from dp_flyweight import Documento, FabricaEstilos


class TestFlyweight(unittest.TestCase):
    def test_compartilha_instancias(self):
        f = FabricaEstilos()
        self.assertIs(f.obter("Arial", 12), f.obter("Arial", 12))
        self.assertIsNot(f.obter("Arial", 12), f.obter("Arial", 14))
        self.assertEqual(f.total(), 2)

    def test_documento_reaproveita(self):
        f = FabricaEstilos()
        d = Documento(f)
        d.escrever("ola ")
        d.escrever("mundo", negrito=True)
        d.escrever(" fim")
        self.assertEqual(d.texto(), "ola mundo fim")
        self.assertEqual(f.total(), 2)
        self.assertIs(d.estilo_em(0), d.estilo_em(10))
        self.assertTrue(d.estilo_em(5).negrito)

    def test_imutavel(self):
        e = FabricaEstilos().obter("A", 1)
        with self.assertRaises(Exception):
            e.tamanho = 5


if __name__ == "__main__":
    unittest.main()
