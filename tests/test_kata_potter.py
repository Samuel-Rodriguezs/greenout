import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from kata_potter import preco


class TestKataPotter(unittest.TestCase):
    def test_vazio(self):
        self.assertEqual(preco([]), 0)

    def test_um_livro(self):
        self.assertEqual(preco([1]), 800)

    def test_iguais_sem_desconto(self):
        self.assertEqual(preco([2, 2]), 1600)
        self.assertEqual(preco([2, 2, 2]), 2400)

    def test_descontos_simples(self):
        self.assertEqual(preco([1, 2]), 1520)
        self.assertEqual(preco([1, 2, 3]), 2160)
        self.assertEqual(preco([1, 2, 3, 4]), 2560)
        self.assertEqual(preco([1, 2, 3, 4, 5]), 3000)

    def test_conjuntos_mistos(self):
        self.assertEqual(preco([1, 1, 2]), 800 + 1520)
        self.assertEqual(preco([1, 1, 2, 2]), 2 * 1520)
        self.assertEqual(preco([1, 1, 2, 3, 3, 4]), 1520 + 2560)
        self.assertEqual(preco([1, 2, 2, 3, 4, 5]), 800 + 3000)

    def test_caso_otimo_nao_guloso(self):
        # dois conjuntos de 4 (5120) batem 5+3 (5160)
        livros = [1, 1, 2, 2, 3, 3, 4, 5]
        self.assertEqual(preco(livros), 2 * 2560)

    def test_caso_grande(self):
        self.assertEqual(preco([1, 2, 3, 4, 5] * 5), 5 * 3000)
        self.assertEqual(preco([1, 2, 3, 4, 5] * 4 + [1, 2, 3]), 3 * 3000 + 2 * 2560)  # 5+3 vira 4+4

    def test_ordem_nao_importa(self):
        self.assertEqual(preco([5, 3, 1, 3, 2, 4, 2, 1]), preco([1, 1, 2, 2, 3, 3, 4, 5]))

    def test_invalido(self):
        with self.assertRaises(ValueError):
            preco([6])


if __name__ == "__main__":
    unittest.main()
