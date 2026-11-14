import sys
import unittest
from collections import Counter
from datetime import datetime, timedelta, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

import gen_log_http as g


class TestGenLogHttp(unittest.TestCase):
    def test_determinismo(self):
        self.assertEqual(g.gerar_linhas(1, 100), g.gerar_linhas(1, 100))
        self.assertNotEqual(g.gerar_linhas(1, 100), g.gerar_linhas(2, 100))

    def test_todas_as_linhas_casam_com_o_formato(self):
        for l in g.gerar_linhas(3, 500):
            d = g.interpretar_linha(l)
            self.assertIn(d["metodo"], {"GET", "POST", "PUT", "DELETE"})
            self.assertEqual(d["versao"], "HTTP/1.1")
            self.assertTrue(str(d["caminho"]).startswith("/"))
            self.assertTrue(100 <= d["status"] <= 599)

    def test_304_sem_corpo(self):
        for l in g.gerar_linhas(4, 1000):
            d = g.interpretar_linha(l)
            if d["status"] == 304:
                self.assertEqual(d["tamanho"], 0)
                self.assertIn('HTTP/1.1" 304 - "', l)

    def test_distribuicao_aproximada(self):
        c = Counter(g.interpretar_linha(l)["metodo"] for l in g.gerar_linhas(5, 5000))
        self.assertGreater(c["GET"], 3500)
        self.assertGreater(c["POST"], c["PUT"])

    def test_formatar_data(self):
        t = datetime(2025, 3, 10, 13, 5, 9, tzinfo=timezone(timedelta(hours=-3)))
        self.assertEqual(g.formatar_data(t), "10/Mar/2025:13:05:09 -0300")
        t2 = datetime(2025, 12, 1, 0, 0, 0, tzinfo=timezone(timedelta(hours=5, minutes=30)))
        self.assertEqual(g.formatar_data(t2), "01/Dec/2025:00:00:00 +0530")

    def test_ordem_cronologica(self):
        datas = [
            datetime.strptime(g.interpretar_linha(l)["data"], "%d/%b/%Y:%H:%M:%S %z")
            for l in g.gerar_linhas(6, 300)
        ]
        self.assertEqual(datas, sorted(datas))

    def test_erros(self):
        with self.assertRaises(ValueError):
            g.interpretar_linha("lixo")
        with self.assertRaises(ValueError):
            g.gerar_linhas(1, 1, datetime(2025, 1, 1))


if __name__ == "__main__":
    unittest.main()
