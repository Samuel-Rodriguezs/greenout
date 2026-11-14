import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from lang_brainfuck import ErroBrainfuck, executar

HELLO = "++++++++[>++++[>++>+++>+++>+<<<<-]>+>+>->>+[<]<-]>>.>---.+++++++..+++.>>.<-.<.+++.------.--------.>>+.>++."


class TestBrainfuck(unittest.TestCase):
    def test_hello_world(self):
        self.assertEqual(executar(HELLO), "Hello World!\n")

    def test_eco(self):
        self.assertEqual(executar(",[.,]", "abc"), "abc")

    def test_wrap(self):
        self.assertEqual(executar("-."), "\xff".encode("latin-1").decode("utf-8", "replace"))

    def test_comentarios_ignorados(self):
        self.assertEqual(executar("soma ++++++++[>++++++++<-]>+. fim"), "A")

    def test_colchete_aberto(self):
        with self.assertRaises(ErroBrainfuck):
            executar("[+")

    def test_colchete_fechado_sem_abrir(self):
        with self.assertRaises(ErroBrainfuck):
            executar("+]")

    def test_ponteiro_negativo(self):
        with self.assertRaises(ErroBrainfuck):
            executar("<")

    def test_laco_infinito(self):
        with self.assertRaises(ErroBrainfuck):
            executar("+[]", max_passos=1000)


if __name__ == "__main__":
    unittest.main()
