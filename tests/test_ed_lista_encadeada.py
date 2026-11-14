import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "python"))

from ed_lista_encadeada import ListaEncadeada


class TestListaEncadeada(unittest.TestCase):
    def test_vazia(self) -> None:
        lista = ListaEncadeada()
        self.assertEqual(len(lista), 0)
        self.assertEqual(list(lista), [])
        self.assertEqual(lista.buscar(1), -1)

    def test_inserir(self) -> None:
        lista = ListaEncadeada()
        lista.inserir_fim(2)
        lista.inserir_inicio(1)
        lista.inserir_fim(3)
        self.assertEqual(list(lista), [1, 2, 3])
        self.assertEqual(len(lista), 3)

    def test_buscar_duplicados_retorna_primeiro(self) -> None:
        lista = ListaEncadeada()
        for v in (5, 7, 5):
            lista.inserir_fim(v)
        self.assertEqual(lista.buscar(5), 0)
        self.assertEqual(lista.buscar(7), 1)

    def test_remover_cabeca_meio_fim(self) -> None:
        lista = ListaEncadeada()
        for v in (1, 2, 3, 4):
            lista.inserir_fim(v)
        lista.remover(1)
        lista.remover(3)
        lista.remover(4)
        self.assertEqual(list(lista), [2])
        self.assertEqual(len(lista), 1)

    def test_remover_inexistente(self) -> None:
        with self.assertRaises(ValueError):
            ListaEncadeada().remover(1)

    def test_remover_so_primeira_ocorrencia(self) -> None:
        lista = ListaEncadeada()
        for v in (1, 1):
            lista.inserir_fim(v)
        lista.remover(1)
        self.assertEqual(list(lista), [1])

    def test_inverter(self) -> None:
        lista = ListaEncadeada()
        lista.inverter()
        self.assertEqual(list(lista), [])
        for v in (1, 2, 3):
            lista.inserir_fim(v)
        lista.inverter()
        self.assertEqual(list(lista), [3, 2, 1])


if __name__ == "__main__":
    unittest.main()
