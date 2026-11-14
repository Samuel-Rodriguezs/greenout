import contextlib
import io
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from cli_senha import main


def rodar(args):
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        code = main(args)
    return code, buf.getvalue().strip().splitlines()


class TestCliSenha(unittest.TestCase):
    def test_seed_reprodutivel(self):
        self.assertEqual(rodar(["--seed", "7"]), rodar(["--seed", "7"]))

    def test_tamanho_e_quantidade(self):
        code, linhas = rodar(["-t", "20", "-n", "3", "--seed", "1"])
        self.assertEqual(code, 0)
        self.assertEqual(len(linhas), 3)
        self.assertTrue(all(len(l) == 20 for l in linhas))

    def test_classes_de_caracteres(self):
        _, linhas = rodar(["-t", "8", "--seed", "3", "--sem-simbolos"])
        s = linhas[0]
        self.assertTrue(any(c.islower() for c in s))
        self.assertTrue(any(c.isupper() for c in s))
        self.assertTrue(any(c.isdigit() for c in s))
        self.assertTrue(s.isalnum())

    def test_tamanho_pequeno(self):
        with contextlib.redirect_stderr(io.StringIO()):
            self.assertEqual(main(["-t", "2"]), 1)


if __name__ == "__main__":
    unittest.main()
