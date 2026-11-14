import json
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from web_erros import ErroHttp, mw_erros, resposta_erro
from web_http import Requisicao, Resposta
from web_middleware import Pipeline
from web_roteador import MetodoNaoPermitido, RotaNaoEncontrada


def pipe(final, **kw):
    return Pipeline(final).usar(mw_erros(**kw))


def req(accept=None):
    return Requisicao("GET", "/", cabecalhos={"Accept": accept} if accept else {})


def levanta(exc):
    def f(r):
        raise exc
    return f


class TestWebErros(unittest.TestCase):
    def test_404_html_por_padrao(self):
        r = pipe(levanta(RotaNaoEncontrada("/x")))(req())
        self.assertEqual(r.status, 404)
        self.assertIn("text/html", r.cabecalhos["content-type"])
        self.assertIn("Página não encontrada", r.texto)

    def test_404_json(self):
        r = pipe(levanta(RotaNaoEncontrada("/x")))(req("application/json"))
        self.assertEqual(json.loads(r.texto)["erro"]["status"], 404)
        self.assertEqual(r.cabecalhos["vary"], "Accept")

    def test_texto_puro(self):
        r = pipe(levanta(ErroHttp(403, "nope")))(req("text/plain"))
        self.assertEqual(r.texto, "403 nope")

    def test_405_com_allow(self):
        r = pipe(levanta(MetodoNaoPermitido(["GET", "POST"])))(req())
        self.assertEqual((r.status, r.cabecalhos["allow"]), (405, "GET, POST"))

    def test_500_nao_vaza_em_producao(self):
        capturados = []
        r = pipe(levanta(RuntimeError("senha=123")), ao_falhar=capturados.append)(req())
        self.assertEqual(r.status, 500)
        self.assertNotIn("senha", r.texto)
        self.assertNotIn("Traceback", r.texto)
        self.assertEqual(len(capturados), 1)

    def test_500_debug_mostra_e_escapa(self):
        r = pipe(levanta(RuntimeError("<script>")), debug=True)(req())
        self.assertIn("Traceback", r.texto)
        self.assertIn("&lt;script&gt;", r.texto)
        self.assertNotIn("<script>", r.texto)

    def test_mensagem_e_escapada(self):
        r = resposta_erro(req(), 400, "<b>x</b>")
        self.assertNotIn("<b>", r.texto)

    def test_erro_http_cabecalhos(self):
        r = pipe(levanta(ErroHttp(401, cabecalhos={"WWW-Authenticate": "Basic"})))(req())
        self.assertEqual(r.cabecalhos["www-authenticate"], "Basic")

    def test_resposta_vazia_de_erro_ganha_pagina(self):
        r = pipe(lambda q: Resposta(404))(req())
        self.assertIn("404", r.texto)

    def test_sucesso_passa(self):
        self.assertEqual(pipe(lambda q: Resposta.de_texto("ok"))(req()).texto, "ok")

    def test_status_invalido(self):
        with self.assertRaises(ValueError):
            ErroHttp(200)


if __name__ == "__main__":
    unittest.main()
