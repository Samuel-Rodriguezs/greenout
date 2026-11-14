import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from util_duracao import formatar_duracao, interpretar_duracao


class TestDuracao(unittest.TestCase):
    def test_formatar(self):
        casos = {0: "0s", 59: "59s", 60: "1min 00s", 125: "2min 05s",
                 3600: "1h 00min 00s", 3725: "1h 02min 05s", 90061: "25h 01min 01s"}
        for seg, esperado in casos.items():
            with self.subTest(seg=seg):
                self.assertEqual(formatar_duracao(seg), esperado)

    def test_float_trunca(self):
        self.assertEqual(formatar_duracao(59.9), "59s")

    def test_formatar_invalido(self):
        with self.assertRaises(ValueError):
            formatar_duracao(-1)
        with self.assertRaises(TypeError):
            formatar_duracao("10")
        with self.assertRaises(TypeError):
            formatar_duracao(True)

    def test_interpretar(self):
        self.assertEqual(interpretar_duracao("1h 02min 05s"), 3725)
        self.assertEqual(interpretar_duracao("45s"), 45)
        self.assertEqual(interpretar_duracao("2min"), 120)
        self.assertEqual(interpretar_duracao("1h30min"), 5400)

    def test_interpretar_invalido(self):
        for t in ("", "   ", "abc", "10", "5s 1min"):
            with self.subTest(t=t):
                with self.assertRaises(ValueError):
                    interpretar_duracao(t)

    def test_ida_e_volta(self):
        for seg in (0, 1, 61, 3599, 3600, 100000):
            self.assertEqual(interpretar_duracao(formatar_duracao(seg)), seg)


if __name__ == "__main__":
    unittest.main()
