import base64
import json
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from crip_jwt import JWTInvalido, codificar, decodificar

# Token do exemplo de jwt.io (segredo "your-256-bit-secret").
TOKEN_JWT_IO = (
    "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ."
    "SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c"
)


class TestJwt(unittest.TestCase):
    def test_vetor_conhecido(self):
        payload = {"sub": "1234567890", "name": "John Doe", "iat": 1516239022}
        self.assertEqual(codificar(payload, b"your-256-bit-secret"), TOKEN_JWT_IO)
        self.assertEqual(decodificar(TOKEN_JWT_IO, b"your-256-bit-secret"), payload)

    def test_ida_e_volta_unicode(self):
        p = {"nome": "João", "n": 3}
        self.assertEqual(decodificar(codificar(p, b"k"), b"k"), p)

    def test_segredo_errado_e_adulteracao(self):
        t = codificar({"a": 1}, b"k")
        with self.assertRaises(JWTInvalido):
            decodificar(t, b"outro")
        cab, _, sig = t.split(".")
        corpo = base64.urlsafe_b64encode(b'{"a":2}').rstrip(b"=").decode()
        with self.assertRaises(JWTInvalido):
            decodificar(f"{cab}.{corpo}.{sig}", b"k")

    def test_alg_none_rejeitado(self):
        b = lambda o: base64.urlsafe_b64encode(json.dumps(o).encode()).rstrip(b"=").decode()  # noqa: E731
        with self.assertRaises(JWTInvalido):
            decodificar(f"{b({'alg': 'none'})}.{b({'a': 1})}.", b"k")

    def test_exp_nbf(self):
        t = codificar({"exp": 100, "nbf": 50}, b"k")
        self.assertEqual(decodificar(t, b"k", agora=60)["exp"], 100)
        with self.assertRaises(JWTInvalido):
            decodificar(t, b"k", agora=100)
        with self.assertRaises(JWTInvalido):
            decodificar(t, b"k", agora=10)

    def test_malformado(self):
        for t in ("", "a.b", "a.b.c.d", "!!!.@@@.###"):
            with self.assertRaises(JWTInvalido):
                decodificar(t, b"k")


if __name__ == "__main__":
    unittest.main()
