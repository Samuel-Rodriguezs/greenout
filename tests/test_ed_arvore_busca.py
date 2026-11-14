import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "python"))

from ed_arvore_busca import ArvoreBusca


def montar() -> ArvoreBusca:
    arvore = ArvoreBusca()
    for v in (50, 30, 70, 20, 40, 60, 80):
        arvore.inserir(v)
    return arvore


class TestArvoreBusca(unittest.TestCase):
    def test_vazia(self) -> None:
        arvore = ArvoreBusca()
        self.assertEqual(len(arvore), 0)
        self.assertEqual(arvore.altura(), 0)
        self.assertEqual(arvore.em_ordem(), [])
        self.assertFalse(arvore.buscar(1))

    def test_percursos(self) -> None:
        arvore = montar()
        self.assertEqual(arvore.em_ordem(), [20, 30, 40, 50, 60, 70, 80])
        self.assertEqual(arvore.pre_ordem(), [50, 30, 20, 40, 70, 60, 80])
        self.assertEqual(arvore.pos_ordem(), [20, 40, 30, 60, 80, 70, 50])
        self.assertEqual(arvore.altura(), 3)

    def test_duplicado_ignorado(self) -> None:
        arvore = montar()
        self.assertFalse(arvore.inserir(50))
        self.assertEqual(len(arvore), 7)

    def test_buscar(self) -> None:
        arvore = montar()
        self.assertTrue(arvore.buscar(60))
        self.assertFalse(arvore.buscar(65))

    def test_remover_folha_um_filho_dois_filhos(self) -> None:
        arvore = montar()
        arvore.remover(20)
        arvore.remover(30)
        self.assertEqual(arvore.em_ordem(), [40, 50, 60, 70, 80])
        arvore.remover(50)
        self.assertEqual(arvore.em_ordem(), [40, 60, 70, 80])
        self.assertEqual(len(arvore), 4)

    def test_remover_inexistente(self) -> None:
        with self.assertRaises(KeyError):
            montar().remover(99)

    def test_degenerada(self) -> None:
        arvore = ArvoreBusca()
        for v in range(1, 6):
            arvore.inserir(v)
        self.assertEqual(arvore.altura(), 5)


if __name__ == "__main__":
    unittest.main()
