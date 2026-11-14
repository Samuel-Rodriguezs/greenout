import itertools
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

import sig_hamming74 as h


class TestHamming74(unittest.TestCase):
    def test_palavra_conhecida(self):
        self.assertEqual(h.codificar_nibble([1, 0, 1, 1]), [0, 1, 1, 0, 0, 1, 1])
        self.assertEqual(h.codificar_nibble([0, 0, 0, 0]), [0] * 7)

    def test_sem_erro(self):
        for d in itertools.product((0, 1), repeat=4):
            w = h.codificar_nibble(list(d))
            self.assertEqual(h.sindrome(w), 0)
            self.assertEqual(h.decodificar_palavra(w), (list(d), 0))

    def test_corrige_qualquer_erro_simples(self):
        for d in itertools.product((0, 1), repeat=4):
            w = h.codificar_nibble(list(d))
            for pos in range(7):
                r = list(w)
                r[pos] ^= 1
                self.assertEqual(h.sindrome(r), pos + 1)
                self.assertEqual(h.decodificar_palavra(r), (list(d), pos + 1))

    def test_distancia_minima_3(self):
        palavras = [h.codificar_nibble(list(d)) for d in itertools.product((0, 1), repeat=4)]
        menor = min(
            sum(a != b for a, b in zip(p, q))
            for p, q in itertools.combinations(palavras, 2)
        )
        self.assertEqual(menor, 3)

    def test_erro_duplo_nao_e_corrigido(self):
        w = h.codificar_nibble([1, 1, 0, 0])
        w[0] ^= 1
        w[1] ^= 1
        self.assertNotEqual(h.decodificar_palavra(w)[0], [1, 1, 0, 0])

    def test_bytes_ida_e_volta_com_erros(self):
        msg = "Olá, sinais!".encode()
        bits = h.codificar(msg)
        self.assertEqual(len(bits), 14 * len(msg))
        for i in range(0, len(bits), 7):  # um erro por palavra
            bits[i + (i // 7) % 7] ^= 1
        dados, n = h.decodificar(bits)
        self.assertEqual(dados, msg)
        self.assertEqual(n, len(bits) // 7)

    def test_bits_bytes(self):
        self.assertEqual(h.bytes_para_bits(b"\xa5"), [1, 0, 1, 0, 0, 1, 0, 1])
        self.assertEqual(h.bits_para_bytes([1, 0, 1, 0, 0, 1, 0, 1]), b"\xa5")

    def test_validacao(self):
        with self.assertRaises(ValueError):
            h.codificar_nibble([1, 0, 1])
        with self.assertRaises(ValueError):
            h.sindrome([0] * 6)
        with self.assertRaises(ValueError):
            h.decodificar([0] * 7)
        with self.assertRaises(ValueError):
            h.bits_para_bytes([1] * 5)

    def test_vazio(self):
        self.assertEqual(h.decodificar(h.codificar(b"")), (b"", 0))


if __name__ == "__main__":
    unittest.main()
