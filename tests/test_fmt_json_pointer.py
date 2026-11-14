import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from fmt_json_pointer import ErroPonteiro, consultar, definir, dividir_ponteiro, montar_ponteiro, resolver

DOC = {
    "loja": {"livros": [{"titulo": "A", "preco": 10}, {"titulo": "B", "preco": 20}, {"titulo": "C"}],
             "nome": "Central"},
    "a/b": 1, "m~n": 2, "": 3, " ": 4,
}


class TestFmtJsonPointer(unittest.TestCase):
    def test_rfc6901(self):
        doc = {"foo": ["bar", "baz"], "": 0, "a/b": 1, "c%d": 2, "e^f": 3, "g|h": 4, "i\\j": 5, 'k"l': 6,
               " ": 7, "m~n": 8}
        casos = {"": doc, "/foo": ["bar", "baz"], "/foo/0": "bar", "/": 0, "/a~1b": 1, "/c%d": 2,
                 "/e^f": 3, "/g|h": 4, "/i\\j": 5, '/k"l': 6, "/ ": 7, "/m~0n": 8}
        for p, esperado in casos.items():
            with self.subTest(p=p):
                self.assertEqual(resolver(doc, p), esperado)

    def test_dividir_e_montar(self):
        self.assertEqual(dividir_ponteiro("/a~1b/m~0n/0"), ["a/b", "m~n", "0"])
        self.assertEqual(montar_ponteiro(["a/b", "m~n", 0]), "/a~1b/m~0n/0")

    def test_definir(self):
        novo = definir(DOC, "/loja/nome", "Nova")
        self.assertEqual(novo["loja"]["nome"], "Nova")
        self.assertEqual(DOC["loja"]["nome"], "Central")
        self.assertEqual(len(definir(DOC, "/loja/livros/-", {})["loja"]["livros"]), 4)
        self.assertEqual(definir(DOC, "/loja/livros/0", "x")["loja"]["livros"][0], "x")
        self.assertEqual(definir(DOC, "", 5), 5)

    def test_ponteiro_invalido(self):
        for p in ["a", "/loja/livros/9", "/loja/livros/01", "/loja/livros/x", "/nada", "/loja/nome/x", "/a~2"]:
            with self.subTest(p=p):
                with self.assertRaises(ErroPonteiro):
                    resolver(DOC, p)
        with self.assertRaises(ErroPonteiro):
            definir(DOC, "/loja/livros/9", 1)
        with self.assertRaises(ErroPonteiro):
            definir(DOC, "/loja/nome/x", 1)

    def test_jsonpath_basico(self):
        self.assertEqual(consultar(DOC, "$.loja.nome"), ["Central"])
        self.assertEqual(consultar(DOC, "$.loja.livros[0].titulo"), ["A"])
        self.assertEqual(consultar(DOC, "$.loja.livros[-1].titulo"), ["C"])
        self.assertEqual(consultar(DOC, "$['a/b']"), [1])
        self.assertEqual(consultar(DOC, '$["loja"]["nome"]'), ["Central"])

    def test_jsonpath_curingas_e_fatias(self):
        self.assertEqual(consultar(DOC, "$.loja.livros[*].titulo"), ["A", "B", "C"])
        self.assertEqual(consultar(DOC, "$.loja.livros[0:2].titulo"), ["A", "B"])
        self.assertEqual(consultar(DOC, "$.loja.livros[1:].titulo"), ["B", "C"])
        self.assertEqual(consultar(DOC, "$.loja.livros.*.preco"), [10, 20])
        self.assertEqual(consultar({"a": [1, 2]}, "$.a[:1]"), [1])

    def test_jsonpath_descendentes(self):
        self.assertEqual(consultar(DOC, "$..preco"), [10, 20])
        self.assertEqual(consultar(DOC, "$..titulo"), ["A", "B", "C"])
        self.assertEqual(consultar({"a": {"b": 1}}, "$..*"), [{"b": 1}, 1])

    def test_jsonpath_sem_resultado(self):
        self.assertEqual(consultar(DOC, "$.loja.nada"), [])
        self.assertEqual(consultar(DOC, "$.loja.livros[10]"), [])
        self.assertEqual(consultar(DOC, "$"), [DOC])

    def test_jsonpath_invalido(self):
        for c in ["loja", "$.", "$.loja[", "$.loja[abc]", "$loja", "$..", "$.a b", "$['a'"]:
            with self.subTest(c=c):
                with self.assertRaises(ErroPonteiro):
                    consultar(DOC, c)


if __name__ == "__main__":
    unittest.main()
