import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from web_http import Requisicao, Resposta
from web_middleware import Pipeline
from web_rate_limit import LimitadorJanela, mw_rate_limit


class Rel:
    t = 0.0

    def __call__(self):
        return self.t


class TestWebRateLimit(unittest.TestCase):
    def setUp(self):
        self.rel = Rel()
        self.l = LimitadorJanela(3, 10, self.rel)

    def test_permite_ate_o_limite(self):
        restantes = [self.l.verificar("a").restantes for _ in range(3)]
        self.assertEqual(restantes, [2, 1, 0])
        d = self.l.verificar("a")
        self.assertFalse(d.permitido)
        self.assertEqual(d.retry_apos, 10)

    def test_chaves_independentes(self):
        for _ in range(3):
            self.l.verificar("a")
        self.assertTrue(self.l.verificar("b").permitido)

    def test_janela_desliza(self):
        self.l.verificar("a")           # t=0
        self.rel.t = 4
        self.l.verificar("a")           # t=4
        self.l.verificar("a")           # t=4
        self.rel.t = 9
        d = self.l.verificar("a")
        self.assertFalse(d.permitido)
        self.assertAlmostEqual(d.retry_apos, 1)
        self.rel.t = 10                 # evento de t=0 saiu; só 1 vaga
        self.assertTrue(self.l.verificar("a").permitido)
        self.assertFalse(self.l.verificar("a").permitido)

    def test_negado_nao_consome(self):
        for _ in range(3):
            self.l.verificar("a")
        for _ in range(5):
            self.l.verificar("a")
        self.rel.t = 10
        self.assertTrue(self.l.verificar("a").permitido)

    def test_limpar(self):
        self.l.verificar("a")
        self.rel.t = 11
        self.assertEqual(self.l.limpar(), 1)

    def test_parametros_invalidos(self):
        with self.assertRaises(ValueError):
            LimitadorJanela(0, 1)
        with self.assertRaises(ValueError):
            LimitadorJanela(1, 0)

    def test_middleware_429(self):
        p = Pipeline(lambda r: Resposta(200)).usar(mw_rate_limit(LimitadorJanela(1, 60, self.rel)))
        req = Requisicao("GET", "/", cabecalhos={"X-Forwarded-For": "1.1.1.1"})
        ok = p(req)
        self.assertEqual(ok.status, 200)
        self.assertEqual(ok.cabecalhos["x-ratelimit-remaining"], "0")
        negado = p(req)
        self.assertEqual(negado.status, 429)
        self.assertEqual(negado.cabecalhos["retry-after"], "60")


if __name__ == "__main__":
    unittest.main()
