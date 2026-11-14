import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from fp_lista_persistente import VAZIA, Lista, anexar, de_iteravel, lista


class TestListaPersistente(unittest.TestCase):
    def test_construcao_e_acesso(self):
        l = lista(1, 2, 3)
        self.assertEqual(list(l), [1, 2, 3])
        self.assertEqual(len(l), 3)
        self.assertEqual(l.cabeca, 1)
        self.assertEqual(l.cauda, lista(2, 3))
        self.assertEqual(l[2], 3)
        self.assertEqual(len(VAZIA), 0)
        self.assertTrue(VAZIA.vazia)

    def test_vazia_erros(self):
        with self.assertRaises(IndexError):
            VAZIA.cabeca
        with self.assertRaises(IndexError):
            VAZIA.cauda
        with self.assertRaises(IndexError):
            lista(1)[1]
        with self.assertRaises(IndexError):
            lista(1)[-1]

    def test_imutabilidade_e_compartilhamento(self):
        base = lista(2, 3)
        a = base.cons(1)
        b = base.cons(9)
        self.assertEqual(list(base), [2, 3])
        self.assertIs(a.cauda, base)
        self.assertIs(b.cauda, base)
        with self.assertRaises(AttributeError):
            base.x = 1
        with self.assertRaises(AttributeError):
            base._cabeca = 0

    def test_anexar_compartilha_segunda(self):
        a, b = lista(1, 2), lista(3, 4)
        c = anexar(a, b)
        self.assertEqual(list(c), [1, 2, 3, 4])
        self.assertIs(c.cauda.cauda, b)
        self.assertEqual(list(a + VAZIA), [1, 2])
        self.assertIs(anexar(VAZIA, b), b)

    def test_mapear_filtrar_dobrar(self):
        l = lista(1, 2, 3, 4)
        self.assertEqual(l.mapear(lambda x: x * x), lista(1, 4, 9, 16))
        self.assertEqual(l.filtrar(lambda x: x % 2 == 0), lista(2, 4))
        self.assertEqual(l.dobrar_e(lambda a, x: a - x, 0), -10)
        self.assertEqual(l.dobrar_d(lambda x, a: x - a, 0), -2)
        self.assertEqual(l.dobrar_d(lambda x, a: a + (x,), ()), (4, 3, 2, 1))

    def test_reverter_pegar_largar(self):
        l = lista(1, 2, 3)
        self.assertEqual(l.reverter(), lista(3, 2, 1))
        self.assertEqual(l.reverter().reverter(), l)
        self.assertEqual(l.pegar(2), lista(1, 2))
        self.assertEqual(l.pegar(10), l)
        self.assertEqual(l.pegar(0), VAZIA)
        self.assertEqual(l.largar(1), lista(2, 3))
        self.assertIs(l.largar(1), l.cauda)
        self.assertEqual(l.largar(5), VAZIA)

    def test_atualizar(self):
        l = lista(1, 2, 3, 4)
        n = l.atualizar(1, 99)
        self.assertEqual(list(n), [1, 99, 3, 4])
        self.assertEqual(list(l), [1, 2, 3, 4])
        self.assertIs(n.largar(2), l.largar(2))
        with self.assertRaises(IndexError):
            l.atualizar(4, 0)

    def test_igualdade_hash_repr(self):
        self.assertEqual(lista(1, 2), lista(1, 2))
        self.assertNotEqual(lista(1, 2), lista(1, 3))
        self.assertNotEqual(lista(1), lista(1, 2))
        self.assertNotEqual(lista(1), [1])
        self.assertEqual(hash(lista(1, 2)), hash(lista(1, 2)))
        self.assertEqual(len({lista(1), lista(1), VAZIA}), 2)
        self.assertEqual(repr(lista(1, "a")), "Lista(1, 'a')")
        self.assertEqual(VAZIA, de_iteravel([]))

    def test_lista_grande_sem_estourar_pilha(self):
        n = 50_000
        l = de_iteravel(range(n))
        self.assertEqual(len(l), n)
        self.assertEqual(l.reverter().cabeca, n - 1)
        self.assertEqual(l, de_iteravel(range(n)))
        self.assertEqual(l.dobrar_e(lambda a, x: a + x, 0), n * (n - 1) // 2)
        self.assertIsInstance(l, Lista)


if __name__ == "__main__":
    unittest.main()
