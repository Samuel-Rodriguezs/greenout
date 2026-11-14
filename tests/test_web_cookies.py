import sys
import unittest
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from web_cookies import SetCookie, parse_cookie, parse_set_cookie


class TestWebCookies(unittest.TestCase):
    def test_parse_cookie(self):
        self.assertEqual(parse_cookie("a=1; b=dois%20x; c=\"q\""),
                         {"a": "1", "b": "dois x", "c": "q"})

    def test_parse_malformado_e_duplicado(self):
        self.assertEqual(parse_cookie("lixo; a=1; a=2; =x"), {"a": "1"})
        self.assertEqual(parse_cookie(""), {})

    def test_serializar(self):
        c = SetCookie("sid", "a b", max_age=60, seguro=True, http_only=True, same_site="lax")
        self.assertEqual(c.serializar(),
                         "sid=a%20b; Max-Age=60; Path=/; Secure; HttpOnly; SameSite=Lax")

    def test_expires_gmt(self):
        c = SetCookie("a", "1", expira=datetime(2030, 1, 2, 3, 4, 5, tzinfo=timezone.utc))
        self.assertIn("Expires=Wed, 02 Jan 2030 03:04:05 GMT", c.serializar())

    def test_remover(self):
        s = SetCookie.remover("sid").serializar()
        self.assertIn("Max-Age=0", s)
        self.assertIn("1970", s)

    def test_roundtrip(self):
        c = SetCookie("k", "v w", max_age=10, dominio="ex.com", seguro=True, same_site="Strict")
        volta = parse_set_cookie(c.serializar())
        self.assertEqual((volta.nome, volta.valor, volta.max_age, volta.dominio),
                         ("k", "v w", 10, "ex.com"))
        self.assertTrue(volta.seguro)
        self.assertEqual(volta.same_site, "Strict")

    def test_erros(self):
        with self.assertRaises(ValueError):
            SetCookie("a b", "1")
        with self.assertRaises(ValueError):
            SetCookie("a", "1", same_site="x")
        with self.assertRaises(ValueError):
            SetCookie("a", "1", same_site="None")
        with self.assertRaises(ValueError):
            parse_set_cookie("semigual")


if __name__ == "__main__":
    unittest.main()
