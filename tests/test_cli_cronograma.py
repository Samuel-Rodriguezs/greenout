import contextlib
import io
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from cli_cronograma import distribuir, main


def rodar(args):
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        code = main(args)
    return code, buf.getvalue().strip().splitlines()


class TestCliCronograma(unittest.TestCase):
    def test_distribuir_soma_total(self):
        r = distribuir({"mat": 3, "port": 2, "hist": 1}, 10)
        self.assertEqual(sum(r.values()), 10)
        self.assertEqual(r["mat"], 5)

    def test_horas_por_dia(self):
        code, linhas = rodar(["mat:1", "port:1", "--inicio", "2024-01-01", "--dias", "2", "--horas-dia", "2"])
        self.assertEqual(code, 0)
        total = sum(int(l.split()[-1].rstrip("h")) for l in linhas)
        self.assertEqual(total, 4)
        self.assertTrue(linhas[0].startswith("2024-01-01"))

    def test_peso_padrao(self):
        code, linhas = rodar(["a", "--inicio", "2024-01-01", "--dias", "1", "--horas-dia", "3"])
        self.assertEqual((code, linhas), (0, ["2024-01-01 a 3h"]))

    def test_erros(self):
        with contextlib.redirect_stderr(io.StringIO()):
            self.assertEqual(main(["a:x"]), 1)
            self.assertEqual(main(["a", "--dias", "0"]), 1)
            self.assertEqual(main(["a", "--inicio", "ontem"]), 1)


if __name__ == "__main__":
    unittest.main()
