import contextlib
import io
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from cli_relogio_mundial import CIDADES, main


def rodar(args):
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        code = main(args)
    return code, buf.getvalue().strip().splitlines()


class TestCliRelogioMundial(unittest.TestCase):
    def test_brasilia_toquio(self):
        code, linhas = rodar(["brasilia", "toquio", "--utc", "2024-01-01T12:00"])
        self.assertEqual(code, 0)
        self.assertEqual(linhas[0], "brasilia: 2024-01-01 09:00 (UTC-03:00)")
        self.assertEqual(linhas[1], "toquio: 2024-01-01 21:00 (UTC+09:00)")

    def test_meia_hora_e_virada_de_dia(self):
        _, linhas = rodar(["nova-delhi", "--utc", "2024-01-01T20:00"])
        self.assertEqual(linhas[0], "nova-delhi: 2024-01-02 01:30 (UTC+05:30)")

    def test_todas(self):
        _, linhas = rodar(["--utc", "2024-06-01T00:00"])
        self.assertEqual(len(linhas), len(CIDADES))

    def test_erros(self):
        with contextlib.redirect_stderr(io.StringIO()):
            self.assertEqual(main(["atlantida"]), 1)
            self.assertEqual(main(["--utc", "xx"]), 1)


if __name__ == "__main__":
    unittest.main()
