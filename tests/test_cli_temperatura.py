import contextlib
import io
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from cli_temperatura import converter, main


def rodar(args):
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        code = main(args)
    return code, buf.getvalue().strip()


class TestCliTemperatura(unittest.TestCase):
    def test_c_para_f(self):
        self.assertEqual(rodar(["100", "C", "F"]), (0, "100°C = 212.00°F"))

    def test_f_para_c_minusculas(self):
        self.assertEqual(rodar(["32", "f", "c"]), (0, "32°F = 0.00°C"))

    def test_kelvin(self):
        self.assertAlmostEqual(converter(0, "C", "K"), 273.15)
        self.assertAlmostEqual(converter(-40, "C", "F"), -40)

    def test_erros(self):
        with contextlib.redirect_stderr(io.StringIO()):
            self.assertEqual(main(["1", "X", "C"]), 1)
            self.assertEqual(main(["-1", "K", "C"]), 1)


if __name__ == "__main__":
    unittest.main()
