import hashlib
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from crip_commitment import cara_ou_coroa, comprometer, revelar_valido


class TestCommitment(unittest.TestCase):
    def test_revelacao(self):
        c = comprometer(b"meu palpite: 42")
        self.assertTrue(revelar_valido(c.valor, b"meu palpite: 42", c.nonce))
        self.assertTrue(revelar_valido(c.valor.upper(), b"meu palpite: 42", c.nonce))

    def test_vinculante(self):
        c = comprometer(b"42")
        self.assertFalse(revelar_valido(c.valor, b"43", c.nonce))
        self.assertFalse(revelar_valido(c.valor, b"42", b"outro-nonce"))
        self.assertFalse(revelar_valido(c.valor, b"42", b""))

    def test_escondendo(self):
        self.assertNotEqual(comprometer(b"x").valor, comprometer(b"x").valor)

    def test_vetor_deterministico(self):
        c = comprometer(b"abc", b"\x01")
        self.assertEqual(c.valor, hashlib.sha256(b"\x00\x01\x01abc").hexdigest())

    def test_sem_ambiguidade_de_fronteira(self):
        a = comprometer(b"bc", b"a")
        self.assertFalse(revelar_valido(a.valor, b"c", b"ab"))

    def test_nonce_invalido(self):
        with self.assertRaises(ValueError):
            comprometer(b"x", b"")

    def test_cara_ou_coroa(self):
        self.assertEqual(cara_ou_coroa("cara", 0), "cara")
        self.assertEqual(cara_ou_coroa("cara", 1), "coroa")
        self.assertEqual(cara_ou_coroa("coroa", 1), "cara")
        with self.assertRaises(ValueError):
            cara_ou_coroa("moeda", 0)


if __name__ == "__main__":
    unittest.main()
