import contextlib
import io
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from cli_juros import main, montante


def rodar(args):
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        code = main(args)
    return code, buf.getvalue().strip().splitlines()


class TestCliJuros(unittest.TestCase):
    def test_simples(self):
        code, linhas = rodar(["--capital", "1000", "--taxa", "10", "--meses", "2"])
        self.assertEqual(code, 0)
        self.assertEqual(linhas, ["Montante: 1210.00", "Investido: 1000.00", "Juros: 210.00"])

    def test_aporte(self):
        self.assertAlmostEqual(montante(0, 0.01, 2, 100), 201.0)

    def test_anual(self):
        _, linhas = rodar(["--capital", "1000", "--taxa", "12", "--meses", "12", "--anual"])
        self.assertEqual(linhas[0], "Montante: 1120.00")

    def test_negativo(self):
        with contextlib.redirect_stderr(io.StringIO()):
            self.assertEqual(main(["--capital", "-1", "--taxa", "1", "--meses", "1"]), 1)


if __name__ == "__main__":
    unittest.main()
