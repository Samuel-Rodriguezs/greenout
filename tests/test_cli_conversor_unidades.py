import contextlib
import io
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from cli_conversor_unidades import converter, main


def rodar(args):
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        code = main(args)
    return code, buf.getvalue().strip()


class TestCliConversorUnidades(unittest.TestCase):
    def test_km_para_m(self):
        self.assertEqual(rodar(["2", "km", "m"]), (0, "2 km = 2000 m"))

    def test_massa(self):
        self.assertAlmostEqual(converter(1, "kg", "g"), 1000)

    def test_incompativel(self):
        err = io.StringIO()
        with contextlib.redirect_stderr(err):
            code, _ = rodar(["1", "kg", "m"])
        self.assertEqual(code, 1)
        self.assertIn("incompatíveis", err.getvalue())

    def test_desconhecida(self):
        with self.assertRaises(ValueError):
            converter(1, "xx", "m")


if __name__ == "__main__":
    unittest.main()
