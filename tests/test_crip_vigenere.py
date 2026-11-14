import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from crip_vigenere import cifrar, decifrar, estimar_tamanho_chave, indice_coincidencia, quebrar

TEXTO = (
    "It was the best of times, it was the worst of times, it was the age of wisdom, it was the age of "
    "foolishness, it was the epoch of belief, it was the epoch of incredulity, it was the season of Light, "
    "it was the season of Darkness, it was the spring of hope, it was the winter of despair, we had "
    "everything before us, we had nothing before us, we were all going direct to Heaven, we were all going "
    "direct the other way. In short, the period was so far like the present period, that some of its noisiest "
    "authorities insisted on its being received, for good or for evil, in the superlative degree of comparison only."
)


class TestVigenere(unittest.TestCase):
    def test_vetor_classico(self):
        self.assertEqual(cifrar("ATTACKATDAWN", "LEMON"), "LXFOPVEFRNHR")
        self.assertEqual(decifrar("LXFOPVEFRNHR", "LEMON"), "ATTACKATDAWN")

    def test_preserva_nao_letras_e_caixa(self):
        c = cifrar("Hello, World!", "key")
        self.assertEqual(c, "Rijvs, Uyvjn!")
        self.assertEqual(decifrar(c, "KEY"), "Hello, World!")

    def test_chave_invalida(self):
        for k in ("", "ab1", "a b"):
            with self.assertRaises(ValueError):
                cifrar("x", k)

    def test_ic(self):
        self.assertGreater(indice_coincidencia(TEXTO), 0.06)
        self.assertLess(indice_coincidencia(cifrar(TEXTO, "SECRET")), 0.05)
        self.assertEqual(indice_coincidencia("a"), 0.0)

    def test_quebra(self):
        cif = cifrar(TEXTO, "CRYPTO")
        self.assertEqual(estimar_tamanho_chave(cif), 6)
        chave, claro = quebrar(cif)
        self.assertEqual(chave, "CRYPTO")
        self.assertEqual(claro, TEXTO)

    def test_quebra_curto(self):
        with self.assertRaises(ValueError):
            quebrar("a")


if __name__ == "__main__":
    unittest.main()
