import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from fmt_log_apache import ErroLog, estatisticas, parse_linha, parse_log

L1 = '127.0.0.1 - frank [10/Oct/2023:13:55:36 -0300] "GET /index.html HTTP/1.1" 200 2326 "http://ex.com/" "Mozilla/5.0 (X11)"'
L2 = '10.0.0.2 - - [10/Oct/2023:13:56:00 +0000] "POST /api HTTP/1.1" 500 - "-" "curl/8.0"'
L3 = '127.0.0.1 - - [10/Oct/2023:13:57:00 +0000] "GET /index.html HTTP/1.1" 404 10'


class TestFmtLogApache(unittest.TestCase):
    def test_linha_completa(self):
        r = parse_linha(L1)
        self.assertEqual((r.ip, r.usuario, r.metodo, r.caminho, r.status, r.bytes_),
                         ("127.0.0.1", "frank", "GET", "/index.html", 200, 2326))
        self.assertEqual(r.referer, "http://ex.com/")
        self.assertEqual(r.momento.hour, 13)
        self.assertEqual(r.momento.utcoffset().total_seconds(), -3 * 3600)

    def test_campos_vazios_e_formato_comum(self):
        r = parse_linha(L2)
        self.assertEqual((r.usuario, r.bytes_, r.referer, r.user_agent), (None, 0, None, "curl/8.0"))
        r3 = parse_linha(L3)
        self.assertIsNone(r3.user_agent)

    def test_requisicao_invalida_8(self):
        r = parse_linha('1.1.1.1 - - [10/Oct/2023:13:55:36 +0000] "-" 408 0')
        self.assertEqual(r.metodo, "-")

    def test_estatisticas(self):
        e = estatisticas(parse_log([L1, L2, "", L3]))
        self.assertEqual(e["total"], 3)
        self.assertEqual(e["bytes"], 2336)
        self.assertEqual(e["por_classe"], {"2xx": 1, "4xx": 1, "5xx": 1})
        self.assertEqual(e["top_caminhos"][0], ("/index.html", 2))
        self.assertEqual(e["top_ips"][0], ("127.0.0.1", 2))
        self.assertAlmostEqual(e["taxa_erro"], 2 / 3)
        self.assertEqual(e["ips_unicos"], 2)

    def test_estatisticas_vazio(self):
        self.assertEqual(estatisticas([])["total"], 0)

    def test_malformadas(self):
        for ruim in ["", "lixo", '1.1.1.1 - - [32/Oct/2023:13:55:36 +0000] "GET / HTTP/1.1" 200 1',
                     '1.1.1.1 - - [10/Oct/2023:13:55:36 +0000] "GET /" 200 1',
                     '1.1.1.1 - - [10/Oct/2023:13:55:36 +0000] "GET / HTTP/1.1" abc 1']:
            with self.subTest(ruim=ruim):
                with self.assertRaises(ErroLog):
                    parse_linha(ruim)

    def test_ignorar_invalidas(self):
        self.assertEqual(len(parse_log([L1, "lixo", L2], ignorar_invalidas=True)), 2)
        with self.assertRaises(ErroLog):
            parse_log([L1, "lixo"])


if __name__ == "__main__":
    unittest.main()
