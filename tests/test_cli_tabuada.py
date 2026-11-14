import contextlib
import io
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from cli_tabuada import main, tabuada


def rodar(args):
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        code = main(args)
    return code, buf.getvalue().strip()


class TestCliTabuada(unittest.TestCase):
    def test_padrao(self):
        code, out = rodar(["7"])
        self.assertEqual(code, 0)
        linhas = out.splitlines()
        self.assertEqual(len(linhas), 10)
        self.assertEqual(linhas[-1], "7 x 10 = 70")

    def test_intervalo_e_varios(self):
        _, out = rodar(["2", "3", "--inicio", "1", "--fim", "2"])
        self.assertEqual(out, "2 x 1 = 2\n2 x 2 = 4\n\n3 x 1 = 3\n3 x 2 = 6")

    def test_negativo(self):
        self.assertEqual(tabuada(-2, 1, 2), ["-2 x 1 = -2", "-2 x 2 = -4"])

    def test_intervalo_invalido(self):
        with contextlib.redirect_stderr(io.StringIO()):
            self.assertEqual(main(["2", "--inicio", "5", "--fim", "1"]), 1)


if __name__ == "__main__":
    unittest.main()
