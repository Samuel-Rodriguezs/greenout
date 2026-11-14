import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from txt_idioma import detectar_idioma, frequencias, pontuar


class TestIdioma(unittest.TestCase):
    def test_portugues(self):
        self.assertEqual(detectar_idioma("O rato roeu a roupa do rei de Roma e a rainha ficou muito brava com ele"), "pt")

    def test_ingles(self):
        self.assertEqual(detectar_idioma("The quick brown fox jumps over the lazy dog and then the dog is tired"), "en")

    def test_alemao(self):
        self.assertEqual(detectar_idioma("Der schnelle braune Fuchs springt über den faulen Hund und dann ist er müde"), "de")

    def test_sem_letras(self):
        with self.assertRaises(ValueError):
            detectar_idioma("1234 !!!")

    def test_frequencias_somam_100(self):
        self.assertAlmostEqual(sum(frequencias("Ação é só").values()), 100.0)
        self.assertEqual(frequencias(""), {})

    def test_pontuar_idiomas(self):
        self.assertEqual(set(pontuar("abc")), {"pt", "en", "es", "fr", "de", "it"})


if __name__ == "__main__":
    unittest.main()
