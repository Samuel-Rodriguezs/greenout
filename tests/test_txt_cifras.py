import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from txt_cifras import atbash, morse_codificar, morse_decodificar, vigenere_cifrar, vigenere_decifrar


class TestCifras(unittest.TestCase):
    def test_vigenere_classico(self):
        self.assertEqual(vigenere_cifrar("ATTACKATDAWN", "LEMON"), "LXFOPVEFRNHR")
        self.assertEqual(vigenere_decifrar("LXFOPVEFRNHR", "LEMON"), "ATTACKATDAWN")

    def test_vigenere_preserva_caixa_e_simbolos(self):
        c = vigenere_cifrar("Olá, Mundo!", "chave")
        self.assertEqual(vigenere_decifrar(c, "chave"), "Olá, Mundo!")
        self.assertEqual(c[2], "á")

    def test_vigenere_chave_invalida(self):
        for chave in ("", "a1", "çb"):
            with self.assertRaises(ValueError):
                vigenere_cifrar("abc", chave)

    def test_atbash(self):
        self.assertEqual(atbash("abc XYZ!"), "zyx CBA!")
        self.assertEqual(atbash(atbash("Texto Qualquer")), "Texto Qualquer")

    def test_morse(self):
        self.assertEqual(morse_codificar("SOS"), "... --- ...")
        self.assertEqual(morse_codificar("oi mundo"), "--- .. / -- ..- -. -.. ---")
        self.assertEqual(morse_decodificar("--- .. / -- ..- -. -.. ---"), "OI MUNDO")

    def test_morse_acentos_e_vazio(self):
        self.assertEqual(morse_codificar("Ação"), morse_codificar("acao"))
        self.assertEqual(morse_codificar(""), "")
        self.assertEqual(morse_decodificar(""), "")

    def test_morse_invalido(self):
        with self.assertRaises(ValueError):
            morse_codificar("a#b")
        with self.assertRaises(ValueError):
            morse_decodificar("......-.-.-.")


if __name__ == "__main__":
    unittest.main()
