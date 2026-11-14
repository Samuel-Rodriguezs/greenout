import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from pa_janelas import blocos, execucoes, janela_deslizante


class TestJanelas(unittest.TestCase):
    def test_janela(self):
        self.assertEqual(list(janela_deslizante([1, 2, 3, 4], 2)), [(1, 2), (2, 3), (3, 4)])

    def test_janela_maior_que_entrada(self):
        self.assertEqual(list(janela_deslizante([1, 2], 3)), [])

    def test_janela_aceita_gerador(self):
        self.assertEqual(list(janela_deslizante(iter("abc"), 3)), [("a", "b", "c")])

    def test_janela_invalida(self):
        with self.assertRaises(ValueError):
            list(janela_deslizante([1], 0))

    def test_blocos(self):
        self.assertEqual(list(blocos(range(5), 2)), [[0, 1], [2, 3], [4]])
        self.assertEqual(list(blocos([], 3)), [])

    def test_blocos_invalido(self):
        with self.assertRaises(ValueError):
            list(blocos([1], -1))

    def test_execucoes(self):
        self.assertEqual(execucoes("aabccc"), [("a", 2), ("b", 1), ("c", 3)])
        self.assertEqual(execucoes([]), [])


if __name__ == "__main__":
    unittest.main()
