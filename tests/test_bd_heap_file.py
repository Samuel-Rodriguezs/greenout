import os
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from bd_heap_file import RID, HeapFile


class TestHeapFile(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.TemporaryDirectory()
        self.caminho = os.path.join(self.dir.name, "tabela.heap")

    def tearDown(self):
        self.dir.cleanup()

    def test_inserir_ler_e_varrer(self):
        with HeapFile(self.caminho, 128) as h:
            rids = [h.inserir(f"registro-{i}".encode()) for i in range(30)]
            self.assertGreater(h.n_paginas, 1)
            for i, r in enumerate(rids):
                self.assertEqual(h.ler(r), f"registro-{i}".encode())
            self.assertEqual([r for r, _ in h.varrer()], rids)

    def test_persistencia_apos_reabrir(self):
        with HeapFile(self.caminho, 128) as h:
            r = h.inserir(b"persistente")
        with HeapFile(self.caminho, 128) as h:
            self.assertEqual(h.ler(r), b"persistente")
            r2 = h.inserir(b"outro")
            self.assertEqual(h.ler(r2), b"outro")

    def test_remover_e_reuso_de_espaco(self):
        with HeapFile(self.caminho, 128) as h:
            r = h.inserir(b"a" * 60)
            h.inserir(b"b" * 30)
            h.remover(r)
            with self.assertRaises(KeyError):
                h.ler(r)
            paginas = h.n_paginas
            h.inserir(b"c" * 60)
            self.assertEqual(h.n_paginas, paginas)

    def test_atualizar_in_place_e_com_movimento(self):
        with HeapFile(self.caminho, 128) as h:
            r = h.inserir(b"x" * 40)
            h.inserir(b"y" * 60)
            self.assertEqual(h.atualizar(r, b"z" * 10), r)
            self.assertEqual(h.ler(r), b"z" * 10)
            novo = h.atualizar(r, b"w" * 100)
            self.assertNotEqual(novo, r)
            self.assertEqual(h.ler(novo), b"w" * 100)
            with self.assertRaises(KeyError):
                h.ler(r)

    def test_registro_grande_demais(self):
        with HeapFile(self.caminho, 128) as h:
            with self.assertRaises(ValueError):
                h.inserir(b"x" * 500)

    def test_rid_invalido(self):
        with HeapFile(self.caminho, 128) as h:
            h.inserir(b"a")
            with self.assertRaises(IndexError):
                h.ler(RID(9, 0))
            with self.assertRaises(IndexError):
                h.ler(RID(0, 9))

    def test_arquivo_truncado_e_rejeitado(self):
        with HeapFile(self.caminho, 128) as h:
            h.inserir(b"a")
        with open(self.caminho, "ab") as f:
            f.write(b"lixo")
        with self.assertRaises(ValueError):
            HeapFile(self.caminho, 128)


if __name__ == "__main__":
    unittest.main()
