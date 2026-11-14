import contextlib
import io
import sys
import unittest
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from cli_dias_entre import dias_entre, main


def rodar(args):
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        code = main(args)
    return code, buf.getvalue().strip()


class TestCliDiasEntre(unittest.TestCase):
    def test_simples(self):
        self.assertEqual(rodar(["2024-01-01", "2024-03-01"]), (0, "60 dias"))

    def test_negativo(self):
        self.assertEqual(rodar(["2024-01-10", "2024-01-01"]), (0, "-9 dias"))

    def test_uteis(self):
        # segunda 2024-01-01 até segunda 2024-01-08: 5 úteis
        self.assertEqual(dias_entre(date(2024, 1, 1), date(2024, 1, 8), True), 5)
        self.assertEqual(rodar(["2024-01-01", "2024-01-08", "--uteis"]), (0, "5 dias úteis"))

    def test_formato_invalido(self):
        with contextlib.redirect_stderr(io.StringIO()):
            self.assertEqual(main(["01/01/2024", "2024-01-02"]), 1)


if __name__ == "__main__":
    unittest.main()
