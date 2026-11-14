import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from dp_command import ApagarFim, Editor, Historico, Inserir


class TestCommand(unittest.TestCase):
    def setUp(self):
        self.ed = Editor()
        self.h = Historico(self.ed)

    def test_executar_e_desfazer(self):
        self.h.executar(Inserir("ola"))
        self.h.executar(Inserir(" mundo"))
        self.assertEqual(self.ed.texto, "ola mundo")
        self.h.desfazer()
        self.assertEqual(self.ed.texto, "ola")

    def test_apagar_restaura(self):
        self.h.executar(Inserir("abcdef"))
        self.h.executar(ApagarFim(4))
        self.assertEqual(self.ed.texto, "ab")
        self.h.desfazer()
        self.assertEqual(self.ed.texto, "abcdef")

    def test_refazer(self):
        self.h.executar(Inserir("x"))
        self.h.desfazer()
        self.assertTrue(self.h.refazer())
        self.assertEqual(self.ed.texto, "x")

    def test_novo_comando_limpa_refazer(self):
        self.h.executar(Inserir("a"))
        self.h.desfazer()
        self.h.executar(Inserir("b"))
        self.assertFalse(self.h.refazer())

    def test_vazio(self):
        self.assertFalse(self.h.desfazer())

    def test_apagar_mais_que_existe(self):
        self.h.executar(Inserir("ab"))
        self.h.executar(ApagarFim(10))
        self.assertEqual(self.ed.texto, "")
        self.h.desfazer()
        self.assertEqual(self.ed.texto, "ab")


if __name__ == "__main__":
    unittest.main()
