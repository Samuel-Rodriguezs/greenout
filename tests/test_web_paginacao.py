import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from web_paginacao import (codificar_cursor, decodificar_cursor, paginar, paginar_cursor,
                           parse_parametros)


class TestWebPaginacao(unittest.TestCase):
    def test_offset(self):
        p = paginar(list(range(25)), 2, 10)
        self.assertEqual(p.itens, list(range(10, 20)))
        self.assertEqual(p.paginas, 3)
        self.assertTrue(p.tem_proxima and p.tem_anterior)
        self.assertEqual(p.meta()["total"], 25)

    def test_ultima_pagina_parcial_e_alem(self):
        self.assertEqual(paginar(list(range(25)), 3, 10).itens, [20, 21, 22, 23, 24])
        p = paginar(list(range(5)), 9, 10)
        self.assertEqual(p.itens, [])
        self.assertFalse(p.tem_proxima)

    def test_vazio(self):
        p = paginar([], 1, 10)
        self.assertEqual((p.paginas, p.tem_proxima, p.tem_anterior), (1, False, False))

    def test_invalidos(self):
        with self.assertRaises(ValueError):
            paginar([1], 0, 10)
        with self.assertRaises(ValueError):
            paginar([1], 1, 0)
        with self.assertRaises(ValueError):
            paginar([1], 1, 101)

    def test_parse_parametros(self):
        self.assertEqual(parse_parametros({}), (1, 20))
        self.assertEqual(parse_parametros({"pagina": ["3"], "por_pagina": ["500"]}), (3, 100))
        with self.assertRaises(ValueError):
            parse_parametros({"pagina": ["x"]})

    def test_cursor_percorre_tudo(self):
        itens = [{"id": i} for i in range(1, 8)]
        vistos, cur = [], None
        while True:
            pag, cur = paginar_cursor(itens, lambda x: x["id"], 3, cur)
            vistos += [x["id"] for x in pag]
            if cur is None:
                break
        self.assertEqual(vistos, [1, 2, 3, 4, 5, 6, 7])

    def test_cursor_estavel_com_insercao(self):
        itens = [1, 2, 3, 4, 5, 6]
        _, cur = paginar_cursor(itens, lambda x: x, 3)
        itens.insert(0, 0)
        pag, _ = paginar_cursor(itens, lambda x: x, 3, cur)
        self.assertEqual(pag, [4, 5, 6])

    def test_cursor_exato_sem_proximo(self):
        pag, cur = paginar_cursor([1, 2, 3], lambda x: x, 3)
        self.assertEqual((pag, cur), ([1, 2, 3], None))

    def test_cursor_invalido(self):
        with self.assertRaises(ValueError):
            paginar_cursor([1], lambda x: x, 1, "@@@")
        with self.assertRaises(ValueError):
            paginar_cursor([1], lambda x: x, 0)
        self.assertEqual(decodificar_cursor(codificar_cursor(["a", 1])), ["a", 1])


if __name__ == "__main__":
    unittest.main()
