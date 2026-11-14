import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "python"))

from ed_tabela_hash import TabelaHash


class Colisao:
    """Chave cujo hash é sempre igual, para forçar colisões."""

    def __init__(self, nome: str) -> None:
        self.nome = nome

    def __hash__(self) -> int:
        return 1

    def __eq__(self, outro: object) -> bool:
        return isinstance(outro, Colisao) and outro.nome == self.nome


class TestTabelaHash(unittest.TestCase):
    def test_vazia(self) -> None:
        tabela = TabelaHash()
        self.assertEqual(len(tabela), 0)
        self.assertNotIn("a", tabela)
        with self.assertRaises(KeyError):
            tabela.obter("a")

    def test_capacidade_invalida(self) -> None:
        with self.assertRaises(ValueError):
            TabelaHash(0)

    def test_colocar_e_obter(self) -> None:
        tabela = TabelaHash()
        tabela.colocar("a", 1)
        self.assertEqual(tabela.obter("a"), 1)
        self.assertIn("a", tabela)

    def test_chave_duplicada_sobrescreve(self) -> None:
        tabela = TabelaHash()
        tabela.colocar("a", 1)
        tabela.colocar("a", 2)
        self.assertEqual(len(tabela), 1)
        self.assertEqual(tabela.obter("a"), 2)

    def test_remover(self) -> None:
        tabela = TabelaHash()
        tabela.colocar("a", 1)
        self.assertEqual(tabela.remover("a"), 1)
        self.assertEqual(len(tabela), 0)
        with self.assertRaises(KeyError):
            tabela.remover("a")

    def test_colisoes(self) -> None:
        tabela = TabelaHash()
        a, b = Colisao("a"), Colisao("b")
        tabela.colocar(a, 1)
        tabela.colocar(b, 2)
        self.assertEqual(tabela.obter(a), 1)
        self.assertEqual(tabela.obter(b), 2)
        tabela.remover(a)
        self.assertEqual(tabela.obter(b), 2)

    def test_redimensionamento_preserva_itens(self) -> None:
        tabela = TabelaHash(2)
        for i in range(100):
            tabela.colocar(i, i * i)
        self.assertEqual(len(tabela), 100)
        for i in range(100):
            self.assertEqual(tabela.obter(i), i * i)
        self.assertEqual(sorted(k for k, _ in tabela.itens()), list(range(100)))


if __name__ == "__main__":
    unittest.main()
