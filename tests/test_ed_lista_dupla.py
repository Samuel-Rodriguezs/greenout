import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "python"))

from ed_lista_dupla import ListaDupla


class TestListaDupla(unittest.TestCase):
    def test_vazia(self) -> None:
        lista = ListaDupla()
        self.assertEqual(len(lista), 0)
        with self.assertRaises(IndexError):
            lista.remover_inicio()
        with self.assertRaises(IndexError):
            lista.remover_fim()

    def test_adicionar_e_reversa(self) -> None:
        lista = ListaDupla()
        lista.adicionar_fim(2)
        lista.adicionar_fim(3)
        lista.adicionar_inicio(1)
        self.assertEqual(list(lista), [1, 2, 3])
        self.assertEqual(list(lista.reversa()), [3, 2, 1])

    def test_remover_extremidades(self) -> None:
        lista = ListaDupla()
        for v in (1, 2, 3):
            lista.adicionar_fim(v)
        self.assertEqual(lista.remover_inicio(), 1)
        self.assertEqual(lista.remover_fim(), 3)
        self.assertEqual(list(lista), [2])
        self.assertEqual(list(lista.reversa()), [2])

    def test_esvaziar_e_reutilizar(self) -> None:
        lista = ListaDupla()
        lista.adicionar_fim(1)
        lista.remover(1)
        self.assertEqual(len(lista), 0)
        lista.adicionar_fim(9)
        self.assertEqual(list(lista.reversa()), [9])

    def test_remover_meio_e_duplicados(self) -> None:
        lista = ListaDupla()
        for v in (1, 2, 2, 3):
            lista.adicionar_fim(v)
        lista.remover(2)
        self.assertEqual(list(lista), [1, 2, 3])
        self.assertEqual(list(lista.reversa()), [3, 2, 1])

    def test_remover_inexistente(self) -> None:
        with self.assertRaises(ValueError):
            ListaDupla().remover(1)


if __name__ == "__main__":
    unittest.main()
