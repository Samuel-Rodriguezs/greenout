import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from pilha import Pilha, parenteses_balanceados


class TestPilha(unittest.TestCase):
    def test_lifo(self):
        p = Pilha()
        p.empilhar(1)
        p.empilhar(2)
        self.assertEqual(p.topo(), 2)
        self.assertEqual(p.desempilhar(), 2)
        self.assertEqual(len(p), 1)

    def test_vazia(self):
        with self.assertRaises(IndexError):
            Pilha().desempilhar()

    def test_parenteses(self):
        self.assertTrue(parenteses_balanceados("{[()]}"))
        self.assertFalse(parenteses_balanceados("([)]"))
        self.assertFalse(parenteses_balanceados("(("))


if __name__ == "__main__":
    unittest.main()
