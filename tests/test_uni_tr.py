import sys
import unittest
from io import StringIO
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from uni_tr import apagar, expandir, main, traduzir


class TestUniTr(unittest.TestCase):
    def test_expandir(self):
        self.assertEqual(expandir("a-e"), "abcde")
        self.assertEqual(expandir("a-c1"), "abc1")
        self.assertEqual(expandir("-a"), "-a")

    def test_intervalo_invalido(self):
        with self.assertRaises(ValueError):
            expandir("z-a")

    def test_traduzir_maiusculas(self):
        self.assertEqual(traduzir("olá mundo", "a-z", "A-Z"), "OLá MUNDO")

    def test_destino_menor_repete_ultimo(self):
        self.assertEqual(traduzir("abc", "abc", "x"), "xxx")

    def test_destino_maior_ignora_excesso(self):
        self.assertEqual(traduzir("ab", "ab", "xyz"), "xy")

    def test_conjuntos_vazios(self):
        with self.assertRaises(ValueError):
            traduzir("a", "", "b")
        with self.assertRaises(ValueError):
            traduzir("a", "a", "")

    def test_apagar(self):
        self.assertEqual(apagar("banana", "an"), "b")
        self.assertEqual(apagar("abc123", "0-9"), "abc")

    def test_main(self):
        s = StringIO()
        self.assertEqual(main(["a-z", "A-Z"], "abc\n", s), 0)
        self.assertEqual(s.getvalue(), "ABC\n")
        s = StringIO()
        self.assertEqual(main(["-d", "b"], "abc", s), 0)
        self.assertEqual(s.getvalue(), "ac")

    def test_main_erros(self):
        self.assertEqual(main([], "", StringIO()), 2)
        self.assertEqual(main(["a"], "", StringIO()), 2)
        self.assertEqual(main(["z-a", "b"], "", StringIO()), 2)


if __name__ == "__main__":
    unittest.main()
