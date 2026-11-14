import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from fp_zipper import Arv, ZipperArvore, ZipperLista


class TestZipperLista(unittest.TestCase):
    def test_vazia_e_roundtrip(self):
        self.assertIsNone(ZipperLista.de_lista([]))
        z = ZipperLista.de_lista([1, 2, 3])
        self.assertEqual(z.foco, 1)
        self.assertEqual(z.para_lista(), [1, 2, 3])

    def test_navegacao_e_bordas(self):
        z = ZipperLista.de_lista("abc")
        self.assertIsNone(z.esquerda())
        z = z.direita().direita()
        self.assertEqual(z.foco, "c")
        self.assertIsNone(z.direita())
        self.assertEqual(z.posicao(), 2)
        self.assertEqual(z.esquerda().direita(), z)
        self.assertEqual(z.inicio().foco, "a")
        self.assertEqual(z.para_lista(), ["a", "b", "c"])

    def test_edicao_persistente(self):
        z = ZipperLista.de_lista([1, 2, 3]).direita()
        z2 = z.modificar(lambda x: x * 10)
        self.assertEqual(z.para_lista(), [1, 2, 3])
        self.assertEqual(z2.para_lista(), [1, 20, 3])
        self.assertEqual(z.definir(0).foco, 0)
        self.assertEqual(z.inserir_esquerda(9).para_lista(), [1, 9, 2, 3])
        self.assertEqual(z.inserir_direita(9).para_lista(), [1, 2, 9, 3])
        self.assertEqual(z.inserir_esquerda(9).foco, 2)

    def test_remover(self):
        z = ZipperLista.de_lista([1, 2, 3]).direita()
        r = z.remover()
        self.assertEqual((r.foco, r.para_lista()), (3, [1, 3]))
        ultimo = z.direita().remover()
        self.assertEqual((ultimo.foco, ultimo.para_lista()), (2, [1, 2]))
        unico = ZipperLista.de_lista([7])
        self.assertIsNone(unico.remover())


class TestZipperArvore(unittest.TestCase):
    def setUp(self):
        #       1
        #      / \
        #     2   3
        #    /
        #   4
        self.t = Arv(1, Arv(2, Arv(4)), Arv(3))

    def test_descer_e_subir(self):
        z = ZipperArvore(self.t)
        self.assertIsNone(z.subir())
        z4 = z.descer_esq().descer_esq()
        self.assertEqual(z4.foco.valor, 4)
        self.assertEqual(z4.profundidade(), 2)
        self.assertIsNone(z4.descer_esq())
        self.assertIsNone(z4.descer_dir())
        self.assertEqual(z4.subir().subir().foco, self.t)
        self.assertIsNone(z.descer_dir().descer_dir())

    def test_modificacao_persistente(self):
        z = ZipperArvore(self.t).descer_esq().descer_esq()
        novo = z.modificar_valor(lambda v: v + 100).para_arvore()
        self.assertEqual(novo, Arv(1, Arv(2, Arv(104)), Arv(3)))
        self.assertEqual(self.t, Arv(1, Arv(2, Arv(4)), Arv(3)))
        self.assertIs(novo.dir, self.t.dir)  # irmão compartilhado

    def test_substituir_e_raiz(self):
        z = ZipperArvore(self.t).descer_dir()
        nova = z.substituir(Arv(30, Arv(31))).para_arvore()
        self.assertEqual(nova.dir, Arv(30, Arv(31)))
        self.assertEqual(z.raiz().foco, self.t)
        with self.assertRaises(ValueError):
            z.substituir(None)

    def test_ida_e_volta_preserva_arvore(self):
        z = ZipperArvore(self.t)
        for caminho in ("ee", "d", "e", ""):
            atual = z
            for c in caminho:
                atual = atual.descer_esq() if c == "e" else atual.descer_dir()
            self.assertEqual(atual.para_arvore(), self.t)


if __name__ == "__main__":
    unittest.main()
