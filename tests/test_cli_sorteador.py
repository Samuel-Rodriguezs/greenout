import contextlib
import io
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from cli_sorteador import main


def rodar(args):
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        code = main(args)
    return code, buf.getvalue().strip().splitlines()


class TestCliSorteador(unittest.TestCase):
    def test_sorteio_sem_repeticao(self):
        code, linhas = rodar(["a", "b", "c", "d", "-n", "3", "--seed", "1"])
        self.assertEqual(code, 0)
        self.assertEqual(len(set(linhas)), 3)
        self.assertTrue(set(linhas) <= {"a", "b", "c", "d"})

    def test_seed(self):
        args = ["a", "b", "c", "d", "e", "-n", "2", "--seed", "42"]
        self.assertEqual(rodar(args), rodar(args))

    def test_times(self):
        code, linhas = rodar(["a", "b", "c", "d", "e", "--times", "2", "--seed", "3"])
        self.assertEqual(code, 0)
        self.assertEqual(len(linhas), 2)
        membros = [m for l in linhas for m in l.split(": ")[1].split(", ")]
        self.assertEqual(sorted(membros), ["a", "b", "c", "d", "e"])

    def test_erros(self):
        with contextlib.redirect_stderr(io.StringIO()):
            self.assertEqual(main(["a", "-n", "2"]), 1)
            self.assertEqual(main(["a", "b", "--times", "3"]), 1)


if __name__ == "__main__":
    unittest.main()
