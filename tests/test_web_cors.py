import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from web_cors import ConfigCors, mw_cors
from web_http import Requisicao, Resposta
from web_middleware import Pipeline


def pipe(cfg):
    return Pipeline(lambda r: Resposta.de_texto("dados")).usar(mw_cors(cfg))


def preflight(origem="https://a.com", metodo="POST", cabs="Content-Type"):
    h = {"Origin": origem, "Access-Control-Request-Method": metodo}
    if cabs:
        h["Access-Control-Request-Headers"] = cabs
    return Requisicao("OPTIONS", "/x", cabecalhos=h)


class TestWebCors(unittest.TestCase):
    def test_sem_origin_passa_direto(self):
        r = pipe(ConfigCors())(Requisicao("GET", "/"))
        self.assertNotIn("access-control-allow-origin", r.cabecalhos)

    def test_preflight_ok(self):
        cfg = ConfigCors(origens=("https://a.com",), credenciais=True, max_age=100)
        r = pipe(cfg)(preflight())
        self.assertEqual(r.status, 204)
        self.assertEqual(r.cabecalhos["access-control-allow-origin"], "https://a.com")
        self.assertEqual(r.cabecalhos["access-control-max-age"], "100")
        self.assertEqual(r.cabecalhos["access-control-allow-credentials"], "true")
        self.assertEqual(r.cabecalhos["vary"], "Origin")
        self.assertIn("POST", r.cabecalhos["access-control-allow-methods"])
        self.assertEqual(r.cabecalhos["access-control-allow-headers"], "Content-Type")

    def test_preflight_origem_negada(self):
        r = pipe(ConfigCors(origens=("https://a.com",)))(preflight("https://evil.com"))
        self.assertEqual(r.status, 403)

    def test_preflight_metodo_e_cabecalho_negados(self):
        p = pipe(ConfigCors())
        self.assertEqual(p(preflight(metodo="TRACE")).status, 405)
        self.assertEqual(p(preflight(cabs="X-Segredo")).status, 403)

    def test_requisicao_simples(self):
        cfg = ConfigCors(origens=("https://a.com",), cabecalhos_expostos=("X-Id",))
        r = pipe(cfg)(Requisicao("GET", "/", cabecalhos={"Origin": "https://a.com"}))
        self.assertEqual(r.texto, "dados")
        self.assertEqual(r.cabecalhos["access-control-allow-origin"], "https://a.com")
        self.assertEqual(r.cabecalhos["access-control-expose-headers"], "X-Id")

    def test_requisicao_simples_origem_negada_sem_headers(self):
        r = pipe(ConfigCors(origens=("https://a.com",)))(
            Requisicao("GET", "/", cabecalhos={"Origin": "https://evil.com"}))
        self.assertNotIn("access-control-allow-origin", r.cabecalhos)
        self.assertEqual(r.cabecalhos["vary"], "Origin")

    def test_curinga(self):
        r = pipe(ConfigCors())(Requisicao("GET", "/", cabecalhos={"Origin": "https://x.com"}))
        self.assertEqual(r.cabecalhos["access-control-allow-origin"], "*")
        self.assertNotIn("vary", r.cabecalhos)

    def test_credenciais_com_curinga_invalido(self):
        with self.assertRaises(ValueError):
            ConfigCors(credenciais=True)

    def test_options_sem_preflight_vai_ao_manipulador(self):
        r = pipe(ConfigCors())(Requisicao("OPTIONS", "/", cabecalhos={"Origin": "https://x.com"}))
        self.assertEqual(r.status, 200)


if __name__ == "__main__":
    unittest.main()
