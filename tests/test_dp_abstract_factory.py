import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from dp_abstract_factory import (FabricaClara, FabricaEscura, fabrica_para,
                                 tela_login)


class TestAbstractFactory(unittest.TestCase):
    def test_familia_consistente(self):
        for tema in ("claro", "escuro"):
            tela = tela_login(fabrica_para(tema))
            self.assertEqual(len(tela), 3)
            self.assertTrue(all(tema in item for item in tela))

    def test_selecao(self):
        self.assertIsInstance(fabrica_para("claro"), FabricaClara)
        self.assertIsInstance(fabrica_para("escuro"), FabricaEscura)

    def test_invalido(self):
        with self.assertRaises(ValueError):
            fabrica_para("neon")


if __name__ == "__main__":
    unittest.main()
