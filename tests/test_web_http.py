import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from web_http import Cabecalhos, Requisicao, Resposta


class TestWebHttp(unittest.TestCase):
    def test_cabecalhos_insensiveis(self):
        c = Cabecalhos({"Content-Type": "a"})
        self.assertEqual(c["content-type"], "a")
        self.assertIn("CONTENT-TYPE", c)
        self.assertIsNone(c.get("x"))
        del c["content-type"]
        self.assertEqual(len(c), 0)

    def test_requisicao_de_url(self):
        r = Requisicao.de_url("get", "/a/b?x=1&x=2&y=3", {"Accept": "*/*"})
        self.assertEqual(r.metodo, "GET")
        self.assertEqual(r.caminho, "/a/b")
        self.assertEqual(r.query["x"], ["1", "2"])
        self.assertEqual(r.arg("y"), "3")
        self.assertEqual(r.arg("z", "d"), "d")
        self.assertEqual(r.cabecalhos["accept"], "*/*")

    def test_json_corpo(self):
        r = Requisicao("POST", "/", corpo='{"a": 1}'.encode())
        self.assertEqual(r.json(), {"a": 1})

    def test_json_invalido(self):
        with self.assertRaises(ValueError):
            Requisicao("POST", "/", corpo=b"{x").json()
        with self.assertRaises(ValueError):
            Requisicao("POST", "/").json()

    def test_resposta_json_e_texto(self):
        r = Resposta.de_json({"ok": "á"}, 201)
        self.assertEqual(r.status, 201)
        self.assertEqual(r.frase, "Created")
        self.assertEqual(r.cabecalhos["content-type"], "application/json")
        self.assertIn("á", r.texto)
        t = Resposta.de_texto("oi")
        self.assertEqual(t.corpo, b"oi")

    def test_redirecionar(self):
        r = Resposta.redirecionar("/x", 301)
        self.assertEqual(r.cabecalhos["location"], "/x")
        with self.assertRaises(ValueError):
            Resposta.redirecionar("/x", 200)

    def test_status_invalido(self):
        with self.assertRaises(ValueError):
            Resposta(status=42)


if __name__ == "__main__":
    unittest.main()
