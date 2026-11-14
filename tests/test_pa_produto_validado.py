import sys
import unittest
from dataclasses import FrozenInstanceError
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from pa_produto_validado import Produto


class TestProduto(unittest.TestCase):
    def test_criacao_e_normalizacao(self):
        p = Produto("  Caneta ", 250, tags=["a", "b"])
        self.assertEqual(p.nome, "Caneta")
        self.assertEqual(p.tags, ("a", "b"))
        self.assertEqual(p.preco, "R$ 2,50")

    def test_preco_com_zero_a_esquerda(self):
        self.assertEqual(Produto("x", 1005).preco, "R$ 10,05")

    def test_invalidos(self):
        with self.assertRaises(ValueError):
            Produto("  ", 1)
        with self.assertRaises(ValueError):
            Produto("a", -1)
        with self.assertRaises(ValueError):
            Produto("a", 1, estoque=-1)
        with self.assertRaises(TypeError):
            Produto("a", 1.5)
        with self.assertRaises(TypeError):
            Produto("a", True)

    def test_imutavel(self):
        with self.assertRaises(FrozenInstanceError):
            Produto("a", 1).nome = "b"

    def test_com_estoque_revalida(self):
        p = Produto("a", 1)
        self.assertEqual(p.com_estoque(5).estoque, 5)
        with self.assertRaises(ValueError):
            p.com_estoque(-1)

    def test_ordenacao_e_hash(self):
        self.assertLess(Produto("a", 5), Produto("b", 1))
        self.assertEqual(len({Produto("a", 1), Produto("a", 1, tags=("z",))}), 1)


if __name__ == "__main__":
    unittest.main()
