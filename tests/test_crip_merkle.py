import hashlib
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from crip_merkle import ArvoreMerkle, verificar_prova


class TestMerkle(unittest.TestCase):
    def test_raiz_de_uma_folha(self):
        a = ArvoreMerkle([b"x"])
        self.assertEqual(a.raiz, hashlib.sha256(b"\x00x").digest())
        self.assertEqual(a.prova(0), [])
        self.assertTrue(verificar_prova(b"x", [], a.raiz))

    def test_raiz_duas_folhas(self):
        l1, l2 = hashlib.sha256(b"\x00a").digest(), hashlib.sha256(b"\x00b").digest()
        self.assertEqual(ArvoreMerkle([b"a", b"b"]).raiz, hashlib.sha256(b"\x01" + l1 + l2).digest())

    def test_provas_todos_tamanhos(self):
        for n in range(1, 20):
            dados = [f"tx{i}".encode() for i in range(n)]
            a = ArvoreMerkle(dados)
            for i, d in enumerate(dados):
                self.assertTrue(verificar_prova(d, a.prova(i), a.raiz), (n, i))

    def test_prova_falsa(self):
        dados = [bytes([i]) for i in range(7)]
        a = ArvoreMerkle(dados)
        p = a.prova(3)
        self.assertFalse(verificar_prova(b"outro", p, a.raiz))
        self.assertFalse(verificar_prova(dados[3], a.prova(2), a.raiz))
        self.assertFalse(verificar_prova(dados[3], p, ArvoreMerkle(dados[:-1]).raiz))

    def test_mudanca_altera_raiz(self):
        self.assertNotEqual(ArvoreMerkle([b"a", b"b", b"c"]).raiz, ArvoreMerkle([b"a", b"b", b"d"]).raiz)

    def test_bordas(self):
        with self.assertRaises(ValueError):
            ArvoreMerkle([])
        with self.assertRaises(IndexError):
            ArvoreMerkle([b"a"]).prova(1)


if __name__ == "__main__":
    unittest.main()
