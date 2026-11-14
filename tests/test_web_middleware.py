import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from web_http import Requisicao, Resposta
from web_middleware import (Pipeline, mw_capturar_erros, mw_exigir_cabecalho, mw_log,
                            mw_tempo)


class TestWebMiddleware(unittest.TestCase):
    def test_ordem_cebola(self):
        ordem: list[str] = []

        def mk(n):
            def mw(req, prox):
                ordem.append(f"entra {n}")
                r = prox(req)
                ordem.append(f"sai {n}")
                return r
            return mw

        p = Pipeline(lambda r: (ordem.append("final"), Resposta.de_texto("ok"))[1])
        p.usar(mk("a")).usar(mk("b"))
        self.assertEqual(p(Requisicao("GET", "/")).texto, "ok")
        self.assertEqual(ordem, ["entra a", "entra b", "final", "sai b", "sai a"])

    def test_sem_middlewares(self):
        self.assertEqual(Pipeline(lambda r: Resposta(204))(Requisicao("GET", "/")).status, 204)

    def test_curto_circuito(self):
        chamado = []
        p = Pipeline(lambda r: chamado.append(1) or Resposta(200))
        p.usar(mw_exigir_cabecalho("X-Token"))
        self.assertEqual(p(Requisicao("GET", "/")).status, 400)
        self.assertEqual(chamado, [])
        ok = p(Requisicao("GET", "/", cabecalhos={"x-token": "1"}))
        self.assertEqual(ok.status, 200)

    def test_capturar_erros(self):
        def final(r):
            raise RuntimeError("segredo")
        resp = Pipeline(final).usar(mw_capturar_erros)(Requisicao("GET", "/"))
        self.assertEqual(resp.status, 500)
        self.assertNotIn("segredo", resp.texto)

    def test_erro_sem_captura_propaga(self):
        def final(r):
            raise RuntimeError("x")
        with self.assertRaises(RuntimeError):
            Pipeline(final)(Requisicao("GET", "/"))

    def test_tempo_e_log(self):
        tempos = iter([1.0, 1.25])
        reg: list[str] = []
        p = Pipeline(lambda r: Resposta(201))
        p.usar(mw_log(reg)).usar(mw_tempo(lambda: next(tempos)))
        resp = p(Requisicao("POST", "/x"))
        self.assertEqual(resp.cabecalhos["x-tempo-ms"], "250.0")
        self.assertEqual(reg, ["POST /x 201"])


if __name__ == "__main__":
    unittest.main()
