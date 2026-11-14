import hashlib
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from crip_senha_hash import hash_senha, precisa_rehash, verificar_senha


class TestSenhaHash(unittest.TestCase):
    def test_ida_e_volta(self):
        h = hash_senha("correto cavalo", 1000)
        self.assertTrue(verificar_senha("correto cavalo", h))
        self.assertFalse(verificar_senha("errado", h))
        self.assertTrue(verificar_senha("", hash_senha("", 10)))

    def test_sal_aleatorio(self):
        self.assertNotEqual(hash_senha("x", 10), hash_senha("x", 10))

    def test_formato_e_vetor(self):
        h = hash_senha("senha", 5, b"\x01" * 4)
        esperado = hashlib.pbkdf2_hmac("sha256", b"senha", b"\x01" * 4, 5).hex()
        self.assertEqual(h, f"pbkdf2_sha256$5$01010101${esperado}")

    def test_unicode(self):
        self.assertTrue(verificar_senha("ação-ñ", hash_senha("ação-ñ", 10)))

    def test_formatos_invalidos(self):
        for ruim in ("", "abc", "md5$1$00$00", "pbkdf2_sha256$x$00$00", "pbkdf2_sha256$1$zz$00", "a$b$c$d$e"):
            self.assertFalse(verificar_senha("x", ruim))

    def test_rehash(self):
        self.assertTrue(precisa_rehash(hash_senha("a", 10), 100))
        self.assertFalse(precisa_rehash(hash_senha("a", 100), 100))
        self.assertTrue(precisa_rehash("lixo"))

    def test_iteracoes_invalidas(self):
        with self.assertRaises(ValueError):
            hash_senha("a", 0)


if __name__ == "__main__":
    unittest.main()
