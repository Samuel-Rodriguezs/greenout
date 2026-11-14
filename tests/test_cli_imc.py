import contextlib
import io
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from cli_imc import calcular_imc, classificar, main


def rodar(args):
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        code = main(args)
    return code, buf.getvalue().strip()


class TestCliImc(unittest.TestCase):
    def test_normal(self):
        self.assertEqual(rodar(["--peso", "70", "--altura", "1.75"]), (0, "IMC: 22.86 (peso normal)"))

    def test_classes(self):
        self.assertEqual(classificar(17), "abaixo do peso")
        self.assertEqual(classificar(27), "sobrepeso")
        self.assertEqual(classificar(32), "obesidade grau I")
        self.assertEqual(classificar(45), "obesidade grau III")

    def test_invalido(self):
        with self.assertRaises(ValueError):
            calcular_imc(0, 1.7)
        with contextlib.redirect_stderr(io.StringIO()):
            self.assertEqual(main(["--peso", "-1", "--altura", "1.7"]), 1)


if __name__ == "__main__":
    unittest.main()
