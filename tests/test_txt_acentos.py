import sys
import unittest
import unicodedata
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from txt_acentos import iguais_sem_acento, normalizar, remover_acentos, slugificar, tem_acentos


class TestAcentos(unittest.TestCase):
    def test_remover(self):
        self.assertEqual(remover_acentos("Ação, coração, pôr, à vontade, ÜBER"), "Acao, coracao, por, a vontade, UBER")

    def test_forma_decomposta(self):
        decomposto = unicodedata.normalize("NFD", "é")
        self.assertEqual(remover_acentos(decomposto), "e")

    def test_normalizar(self):
        self.assertEqual(normalizar("  Olá   MUNDO \n"), "ola mundo")

    def test_slug(self):
        self.assertEqual(slugificar("Ação Rápida!"), "acao-rapida")
        self.assertEqual(slugificar("---"), "")
        self.assertEqual(slugificar(""), "")

    def test_comparar(self):
        self.assertTrue(iguais_sem_acento("Pão", "pao"))
        self.assertFalse(iguais_sem_acento("pão", "pau"))

    def test_tem_acentos(self):
        self.assertTrue(tem_acentos("café"))
        self.assertFalse(tem_acentos("cafe"))
        self.assertFalse(tem_acentos(""))


if __name__ == "__main__":
    unittest.main()
