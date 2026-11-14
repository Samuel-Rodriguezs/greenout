import json
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from web_http import Requisicao, Resposta
from web_roteador import Roteador
from web_wsgi import AppWsgi, chamar, montar_environ, requisicao_de_environ


class TestWebWsgi(unittest.TestCase):
    def setUp(self):
        r = Roteador()

        @r.rota("/ola/<str:nome>")
        def ola(req, nome):
            return {"ola": nome, "q": req.arg("x")}

        @r.rota("/eco", ("POST",))
        def eco(req):
            return Resposta.de_json({"recebido": req.json(), "ct": req.cabecalhos["content-type"],
                                     "tk": req.cabecalhos.get("X-Token")}, 201)

        @r.rota("/quebra")
        def quebra(req):
            raise RuntimeError("segredo")

        @r.rota("/vazio")
        def vazio(req):
            return None

        self.app = AppWsgi(r)

    def test_get_com_query(self):
        status, cab, corpo = chamar(self.app, "GET", "/ola/mundo?x=1")
        self.assertEqual(status, "200 OK")
        self.assertEqual(json.loads(corpo), {"ola": "mundo", "q": "1"})
        self.assertIn(("Content-Length", str(len(corpo))), cab)
        self.assertIn(("Content-Type", "application/json"), cab)

    def test_post_json_e_cabecalhos(self):
        status, _, corpo = chamar(self.app, "POST", "/eco", b'{"a": [1]}',
                                  {"Content-Type": "application/json", "X-Token": "t"})
        self.assertEqual(status, "201 Created")
        self.assertEqual(json.loads(corpo),
                         {"recebido": {"a": [1]}, "ct": "application/json", "tk": "t"})

    def test_404_e_405(self):
        self.assertEqual(chamar(self.app, "GET", "/nada")[0], "404 Not Found")
        status, cab, _ = chamar(self.app, "GET", "/eco")
        self.assertEqual(status, "405 Method Not Allowed")
        self.assertIn(("Allow", "POST"), cab)

    def test_head_sem_corpo(self):
        status, cab, corpo = chamar(self.app, "HEAD", "/ola/x")
        self.assertEqual((status, corpo), ("200 OK", b""))
        self.assertTrue(any(k == "Content-Length" and int(v) > 0 for k, v in cab))

    def test_204_sem_corpo(self):
        status, _, corpo = chamar(self.app, "GET", "/vazio")
        self.assertEqual((status, corpo), ("204 No Content", b""))

    def test_excecao_vira_500_sem_vazar(self):
        status, _, corpo = chamar(self.app, "GET", "/quebra")
        self.assertEqual(status, "500 Internal Server Error")
        self.assertNotIn(b"segredo", corpo)

    def test_json_invalido_vira_400(self):
        # ValueError levantado em req.json() dentro do handler -> 400
        status, _, _ = chamar(self.app, "POST", "/eco", b"{ruim", {"Content-Type": "application/json"})
        self.assertEqual(status, "400 Bad Request")

    def test_content_length_invalido_e_grande(self):
        env = montar_environ("POST", "/eco", b"x")
        env["CONTENT_LENGTH"] = "abc"
        with self.assertRaises(ValueError):
            requisicao_de_environ(env)
        env["CONTENT_LENGTH"] = "-1"
        with self.assertRaises(ValueError):
            requisicao_de_environ(env)
        env["CONTENT_LENGTH"] = "99"
        with self.assertRaises(OverflowError):
            requisicao_de_environ(env, limite=10)

    def test_app_413(self):
        status, _, _ = chamar(self.app, "POST", "/eco", b"x" * 1_000_001)
        self.assertTrue(status.startswith("413"))

    def test_environ_para_requisicao(self):
        env = montar_environ("get", "/a?b=1&b=2", cabecalhos={"X-Forwarded-For": "1.2.3.4"})
        req = requisicao_de_environ(env)
        self.assertEqual((req.metodo, req.caminho), ("GET", "/a"))
        self.assertEqual(req.query["b"], ["1", "2"])
        self.assertEqual(req.cabecalhos["x-forwarded-for"], "1.2.3.4")

    def test_alvo_funcao(self):
        app = AppWsgi(lambda req: Resposta.de_texto(req.caminho))
        self.assertEqual(chamar(app, "GET", "/z")[2], b"/z")


if __name__ == "__main__":
    unittest.main()
