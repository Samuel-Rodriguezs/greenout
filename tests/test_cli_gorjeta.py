import contextlib
import io
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from cli_gorjeta import calcular, main


def rodar(args):
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        code = main(args)
    return code, buf.getvalue().strip().splitlines()


class TestCliGorjeta(unittest.TestCase):
    def test_padrao(self):
        self.assertEqual(rodar(["200"]), (0, ["Gorjeta: 20.00", "Total: 220.00"]))

    def test_divisao(self):
        self.assertEqual(rodar(["100", "-p", "15", "-n", "4"]),
                         (0, ["Gorjeta: 15.00", "Total: 115.00", "Por pessoa: 28.75"]))

    def test_calcular(self):
        self.assertEqual(calcular(50, 0, 2), (0.0, 50.0, 25.0))

    def test_erros(self):
        with contextlib.redirect_stderr(io.StringIO()):
            self.assertEqual(main(["100", "-n", "0"]), 1)
            self.assertEqual(main(["100", "-p", "-1"]), 1)


if __name__ == "__main__":
    unittest.main()
