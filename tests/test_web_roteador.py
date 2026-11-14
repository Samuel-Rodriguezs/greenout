import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from web_http import Requisicao
from web_roteador import MetodoNaoPermitido, RotaNaoEncontrada, Roteador, compilar


class TestWebRoteador(unittest.TestCase):
    def setUp(self):
        self.r = Roteador()

        @self.r.rota("/usuarios/<int:id>")
        def ver(req, id):
            return {"id": id}

        @self.r.rota("/usuarios", ("GET", "POST"))
        def lista(req):
            return "lista"

        @self.r.rota("/arq/<path:resto>")
        def arq(req, resto):
            return resto

        @self.r.rota("/nada")
        def nada(req):
            return None

    def test_param_int(self):
        resp = self.r.despachar(Requisicao("GET", "/usuarios/42"))
        self.assertEqual(resp.status, 200)
        self.assertEqual(resp.texto, '{"id": 42}')

    def test_int_invalido_da_404(self):
        self.assertEqual(self.r.despachar(Requisicao("GET", "/usuarios/abc")).status, 404)

    def test_404(self):
        with self.assertRaises(RotaNaoEncontrada):
            self.r.resolver("GET", "/x")

    def test_405_com_allow(self):
        resp = self.r.despachar(Requisicao("DELETE", "/usuarios"))
        self.assertEqual(resp.status, 405)
        self.assertEqual(resp.cabecalhos["allow"], "GET, POST")
        with self.assertRaises(MetodoNaoPermitido):
            self.r.resolver("PUT", "/usuarios/1")

    def test_head_usa_get(self):
        self.assertEqual(self.r.despachar(Requisicao("HEAD", "/usuarios")).status, 200)

    def test_path_e_204(self):
        self.assertEqual(self.r.despachar(Requisicao("GET", "/arq/a/b.txt")).texto, "a/b.txt")
        self.assertEqual(self.r.despachar(Requisicao("GET", "/nada")).status, 204)

    def test_url_para(self):
        self.assertEqual(self.r.url_para("ver", id=7), "/usuarios/7")
        with self.assertRaises(KeyError):
            self.r.url_para("ver")
        with self.assertRaises(KeyError):
            self.r.url_para("inexistente")

    def test_padroes_invalidos(self):
        with self.assertRaises(ValueError):
            compilar("sem-barra")
        with self.assertRaises(ValueError):
            compilar("/<foo:x>")
        with self.assertRaises(ValueError):
            compilar("/<int:a>/<int:a>")

    def test_retorno_tupla_e_invalido(self):
        self.r.adicionar("/criar", lambda req: ({"a": 1}, 201), ("POST",))
        self.assertEqual(self.r.despachar(Requisicao("POST", "/criar")).status, 201)
        self.r.adicionar("/ruim", lambda req: 3.5)
        with self.assertRaises(TypeError):
            self.r.despachar(Requisicao("GET", "/ruim"))


if __name__ == "__main__":
    unittest.main()
