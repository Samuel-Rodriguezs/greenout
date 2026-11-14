import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from fmt_http_requisicao import ErroHttp, parse


class TestFmtHttpRequisicao(unittest.TestCase):
    def test_get(self):
        r = parse("GET /a?x=1 HTTP/1.1\r\nHost: ex.com\r\nAccept: a\r\nAccept: b\r\n\r\n")
        self.assertEqual((r.metodo, r.alvo, r.versao), ("GET", "/a?x=1", "1.1"))
        self.assertEqual(r.cabecalho("HOST"), "ex.com")
        self.assertEqual(r.cabecalho("accept"), "a, b")
        self.assertEqual(r.corpo, b"")

    def test_post_content_length(self):
        r = parse(b"POST /x HTTP/1.0\r\nContent-Length: 5\r\n\r\nhello-extra")
        self.assertEqual(r.corpo, b"hello")

    def test_chunked(self):
        raw = b"POST / HTTP/1.1\r\nHost: a\r\nTransfer-Encoding: chunked\r\n\r\n4\r\nWiki\r\n5;ext=1\r\npedia\r\n0\r\n\r\n"
        self.assertEqual(parse(raw).corpo, b"Wikipedia")

    def test_continuacao_e_lf(self):
        r = parse("GET / HTTP/1.1\nHost: a\nX-Longo: um\n  dois\n\n")
        self.assertEqual(r.cabecalho("x-longo"), "um dois")

    def test_malformadas(self):
        casos = [
            "", "GET / HTTP/1.1\r\nHost: a\r\n",
            "FOO / HTTP/1.1\r\nHost: a\r\n\r\n",
            "GET /sem-versao\r\nHost: a\r\n\r\n",
            "GET / HTTP/1.1\r\n\r\n",
            "GET / HTTP/1.1\r\nHost a\r\n\r\n",
            "GET / HTTP/1.1\r\nHost : a\r\n\r\n",
            "POST / HTTP/1.1\r\nHost: a\r\nContent-Length: x\r\n\r\n",
            "POST / HTTP/1.1\r\nHost: a\r\nContent-Length: 10\r\n\r\nabc",
            "POST / HTTP/1.1\r\nHost: a\r\nTransfer-Encoding: chunked\r\n\r\nzz\r\n",
            "POST / HTTP/1.1\r\nHost: a\r\nTransfer-Encoding: chunked\r\n\r\n5\r\nab",
            "GET / HTTP/1.0\r\n x: y\r\n\r\n",
        ]
        for ruim in casos:
            with self.subTest(ruim=ruim):
                with self.assertRaises(ErroHttp):
                    parse(ruim)


if __name__ == "__main__":
    unittest.main()
