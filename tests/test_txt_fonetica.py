import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from txt_fonetica import soam_igual, soundex


class TestFonetica(unittest.TestCase):
    def test_classicos(self):
        self.assertEqual(soundex("Robert"), "R163")
        self.assertEqual(soundex("Rupert"), "R163")
        self.assertEqual(soundex("Ashcraft"), "A261")

    def test_variantes_pt(self):
        self.assertTrue(soam_igual("Silva", "Sylva"))
        self.assertTrue(soam_igual("Thiago", "Tiago"))
        self.assertTrue(soam_igual("João", "Joao"))

    def test_diferentes(self):
        self.assertFalse(soam_igual("Maria", "Pedro"))

    def test_preenchimento(self):
        self.assertEqual(soundex("A"), "A000")
        self.assertEqual(soundex("Tiago"), "T200")

    def test_vazio_e_simbolos(self):
        self.assertEqual(soundex(""), "")
        self.assertEqual(soundex("123"), "")
        self.assertFalse(soam_igual("", ""))


if __name__ == "__main__":
    unittest.main()
