import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from web_etag import (aplicar_etag, calcular_etag, corresponde_if_match,
                      corresponde_if_none_match, mw_etag, verificar_precondicao)
from web_http import Requisicao, Resposta
from web_middleware import Pipeline


class TestWebEtag(unittest.TestCase):
    def test_etag_deterministico(self):
        self.assertEqual(calcular_etag(b"a"), calcular_etag(b"a"))
        self.assertNotEqual(calcular_etag(b"a"), calcular_etag(b"b"))
        self.assertTrue(calcular_etag(b"a", fraco=True).startswith('W/"'))

    def test_if_none_match(self):
        e = '"abc"'
        self.assertTrue(corresponde_if_none_match('"abc"', e))
        self.assertTrue(corresponde_if_none_match('"x", W/"abc"', e))
        self.assertTrue(corresponde_if_none_match("*", e))
        self.assertFalse(corresponde_if_none_match('"x"', e))
        self.assertFalse(corresponde_if_none_match(None, e))
        self.assertFalse(corresponde_if_none_match("", e))

    def test_if_match_forte(self):
        self.assertTrue(corresponde_if_match('"a"', '"a"'))
        self.assertFalse(corresponde_if_match('W/"a"', 'W/"a"'))
        self.assertFalse(corresponde_if_match('"b"', '"a"'))

    def test_304(self):
        resp = Resposta.de_texto("conteúdo")
        etag = calcular_etag(resp.corpo)
        req = Requisicao("GET", "/", cabecalhos={"If-None-Match": etag})
        r = aplicar_etag(req, resp, max_age=60)
        self.assertEqual(r.status, 304)
        self.assertEqual(r.corpo, b"")
        self.assertEqual(r.cabecalhos["etag"], etag)
        self.assertEqual(r.cabecalhos["cache-control"], "max-age=60")

    def test_200_quando_diferente(self):
        req = Requisicao("GET", "/", cabecalhos={"If-None-Match": '"velho"'})
        r = aplicar_etag(req, Resposta.de_texto("novo"))
        self.assertEqual(r.status, 200)
        self.assertIn("etag", r.cabecalhos)

    def test_ignora_post_e_erros(self):
        r = aplicar_etag(Requisicao("POST", "/"), Resposta.de_texto("x"))
        self.assertNotIn("etag", r.cabecalhos)
        r = aplicar_etag(Requisicao("GET", "/"), Resposta.de_texto("x", 404))
        self.assertNotIn("etag", r.cabecalhos)

    def test_middleware(self):
        p = Pipeline(lambda r: Resposta.de_texto("oi")).usar(mw_etag())
        primeira = p(Requisicao("GET", "/"))
        segunda = p(Requisicao("GET", "/", cabecalhos={"If-None-Match": primeira.cabecalhos["etag"]}))
        self.assertEqual(segunda.status, 304)

    def test_precondicao(self):
        req = Requisicao("PUT", "/", cabecalhos={"If-Match": '"velho"'})
        self.assertEqual(verificar_precondicao(req, '"novo"').status, 412)
        self.assertIsNone(verificar_precondicao(req, '"velho"'))
        self.assertIsNone(verificar_precondicao(Requisicao("PUT", "/"), '"x"'))


if __name__ == "__main__":
    unittest.main()
