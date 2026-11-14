import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from dp_singleton import Configuracao


class TestSingleton(unittest.TestCase):
    def setUp(self):
        Configuracao.resetar()

    def test_mesma_instancia(self):
        self.assertIs(Configuracao(), Configuracao())

    def test_estado_compartilhado(self):
        Configuracao().definir("modo", "producao")
        self.assertEqual(Configuracao().obter("modo"), "producao")
        self.assertEqual(Configuracao().obter("x", 7), 7)

    def test_resetar_cria_nova(self):
        a = Configuracao()
        a.definir("k", 1)
        Configuracao.resetar()
        self.assertIsNot(a, Configuracao())
        self.assertIsNone(Configuracao().obter("k"))


if __name__ == "__main__":
    unittest.main()
