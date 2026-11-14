import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from web_auth import (codificar_basic, exigir_escopo, hash_senha, mw_basic, mw_bearer,
                      parse_basic, parse_bearer, verificar_senha)
from web_http import Requisicao, Resposta
from web_middleware import Pipeline


def req(auth=None):
    return Requisicao("GET", "/", cabecalhos={"Authorization": auth} if auth else {})


class TestWebAuth(unittest.TestCase):
    def test_parse_basic(self):
        self.assertEqual(parse_basic(codificar_basic("ana", "se:nha")), ("ana", "se:nha"))
        self.assertEqual(parse_basic("basic " + "YW5hOng="), ("ana", "x"))

    def test_parse_basic_invalido(self):
        for h in (None, "", "Basic", "Basic !!!", "Bearer abc", "Basic " + "c2VtZG9pc3BvbnRvcw==",
                  "Basic OnNlbmhh"):
            self.assertIsNone(parse_basic(h), h)

    def test_parse_bearer(self):
        self.assertEqual(parse_bearer("Bearer abc.def"), "abc.def")
        self.assertEqual(parse_bearer("bearer x"), "x")
        for h in (None, "Bearer", "Basic x", "Bearer a b"):
            self.assertIsNone(parse_bearer(h))

    def test_hash_senha(self):
        h = hash_senha("segredo")
        self.assertTrue(verificar_senha("segredo", h))
        self.assertFalse(verificar_senha("outra", h))
        self.assertNotEqual(h, hash_senha("segredo"))
        self.assertFalse(verificar_senha("x", "lixo"))

    def test_middleware_basic(self):
        usuarios = {"ana": hash_senha("123")}
        p = Pipeline(lambda r: Resposta.de_texto(r.contexto["usuario"])).usar(mw_basic(usuarios, "x"))
        ok = p(req(codificar_basic("ana", "123")))
        self.assertEqual((ok.status, ok.texto), (200, "ana"))
        for cab in (None, codificar_basic("ana", "errada"), codificar_basic("zé", "123")):
            r = p(req(cab))
            self.assertEqual(r.status, 401)
            self.assertEqual(r.cabecalhos["www-authenticate"], 'Basic realm="x"')

    def test_middleware_bearer(self):
        tokens = {"tok": {"nome": "ana", "escopos": ["ler"]}}
        p = Pipeline(lambda r: Resposta.de_texto("ok")).usar(mw_bearer(tokens.get))
        self.assertEqual(p(req("Bearer tok")).status, 200)
        r = p(req("Bearer ruim"))
        self.assertEqual(r.status, 401)
        self.assertIn("invalid_token", r.cabecalhos["www-authenticate"])
        self.assertNotIn("error", p(req()).cabecalhos["www-authenticate"])
        self.assertIn("invalid_request", p(req("Token x")).cabecalhos["www-authenticate"])

    def test_escopo(self):
        tokens = {"a": {"escopos": ["ler"]}, "b": {"escopos": ["ler", "escrever"]}}
        p = Pipeline(lambda r: Resposta(200)).usar(mw_bearer(tokens.get)).usar(exigir_escopo("escrever"))
        # ordem: bearer é o mais externo
        self.assertEqual(p(req("Bearer a")).status, 403)
        self.assertEqual(p(req("Bearer b")).status, 200)


if __name__ == "__main__":
    unittest.main()
