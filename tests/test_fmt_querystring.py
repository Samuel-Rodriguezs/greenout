import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from fmt_querystring import ErroQuery, codificar, codificar_valor, decodificar, decodificar_valor


class TestFmtQuerystring(unittest.TestCase):
    def test_codificar_valor(self):
        self.assertEqual(codificar_valor("a b&c=ç"), "a+b%26c%3D%C3%A7")
        self.assertEqual(codificar_valor("A-z_0.~"), "A-z_0.~")

    def test_decodificar_valor(self):
        self.assertEqual(decodificar_valor("a+b%26%C3%A7"), "a b&ç")

    def test_decodificar_basico(self):
        self.assertEqual(decodificar("?a=1&b=x+y&c="), {"a": "1", "b": "x y", "c": ""})

    def test_repetidos_e_colchetes(self):
        self.assertEqual(decodificar("a=1&a=2&a=3"), {"a": ["1", "2", "3"]})
        self.assertEqual(decodificar("t[]=x&t[]=y"), {"t": ["x", "y"]})
        self.assertEqual(decodificar("u[nome]=Ana&u[id]=3"), {"u": {"nome": "Ana", "id": "3"}})

    def test_vazio(self):
        self.assertEqual(decodificar(""), {})
        self.assertEqual(decodificar("&&a=1&"), {"a": "1"})

    def test_ida_e_volta(self):
        d = {"q": "olá mundo", "l": ["1", "2"], "o": {"k": "v&w"}}
        self.assertEqual(decodificar(codificar(d)), d)
        self.assertEqual(codificar({"ok": True, "n": None, "i": 3}), "ok=true&n=&i=3")

    def test_malformadas(self):
        for ruim in ["a=%zz", "a=%4", "=x", "a=%FF", "a[b][c]=1"]:
            with self.subTest(ruim=ruim):
                with self.assertRaises(ErroQuery):
                    decodificar(ruim)
        with self.assertRaises(ErroQuery):
            decodificar("a=1&a[x]=2")


if __name__ == "__main__":
    unittest.main()
