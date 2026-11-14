import contextlib
import io
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from cli_bases import main, para_base


def rodar(args):
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        code = main(args)
    return code, buf.getvalue().strip()


class TestCliBases(unittest.TestCase):
    def test_decimal_binario(self):
        self.assertEqual(rodar(["10"]), (0, "1010"))

    def test_hex_para_decimal(self):
        self.assertEqual(rodar(["ff", "--de", "16", "--para", "10"]), (0, "255"))

    def test_negativo_e_zero(self):
        self.assertEqual(para_base(-255, 16), "-ff")
        self.assertEqual(para_base(0, 2), "0")

    def test_erros(self):
        with contextlib.redirect_stderr(io.StringIO()):
            self.assertEqual(main(["12", "--de", "2"]), 1)
            self.assertEqual(main(["12", "--para", "40"]), 1)


if __name__ == "__main__":
    unittest.main()
