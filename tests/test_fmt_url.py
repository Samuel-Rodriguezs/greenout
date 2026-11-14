import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from fmt_url import ErroUrl, parse


class TestFmtUrl(unittest.TestCase):
    def test_completa(self):
        u = parse("HTTPS://user:p%40ss@Exemplo.com:8443/a/b?x=1&y=a+b&x=2#se%C3%A7%C3%A3o")
        self.assertEqual(u.esquema, "https")
        self.assertEqual((u.usuario, u.senha), ("user", "p@ss"))
        self.assertEqual(u.host, "exemplo.com")
        self.assertEqual(u.porta, 8443)
        self.assertEqual(u.caminho, "/a/b")
        self.assertEqual(u.query, {"x": ["1", "2"], "y": ["a b"]})
        self.assertEqual(u.fragmento, "seção")

    def test_porta_padrao_e_caminho_raiz(self):
        u = parse("http://localhost")
        self.assertIsNone(u.porta)
        self.assertEqual(u.porta_efetiva, 80)
        self.assertEqual(u.caminho, "/")
        self.assertEqual(parse("https://x.com").porta_efetiva, 443)

    def test_ipv6(self):
        u = parse("http://[::1]:3000/p")
        self.assertEqual((u.host, u.porta), ("[::1]", 3000))

    def test_query_sem_valor(self):
        self.assertEqual(parse("http://a.com/?flag&k=").query, {"flag": [""], "k": [""]})

    def test_malformadas(self):
        for ruim in ["", "sem-esquema.com", "http://", "http://a.com:abc/", "http://a.com:99999",
                     "http://[::1/", "http://a.com/?x=%zz", "http://a.com/#%4", "1http://a.com", "http://[::1]x"]:
            with self.subTest(ruim=ruim):
                with self.assertRaises(ErroUrl):
                    parse(ruim)


if __name__ == "__main__":
    unittest.main()
