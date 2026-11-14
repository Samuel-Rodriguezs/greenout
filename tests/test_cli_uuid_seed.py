import contextlib
import io
import sys
import unittest
import uuid
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from cli_uuid_seed import main


def rodar(args):
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        code = main(args)
    return code, buf.getvalue().strip().splitlines()


class TestCliUuidSeed(unittest.TestCase):
    def test_deterministico(self):
        self.assertEqual(rodar(["--seed", "42", "-n", "3"]), rodar(["--seed", "42", "-n", "3"]))

    def test_seeds_diferentes(self):
        self.assertNotEqual(rodar(["--seed", "1"]), rodar(["--seed", "2"]))

    def test_versao_4_valida(self):
        _, linhas = rodar(["--seed", "5", "-n", "4"])
        self.assertEqual(len(set(linhas)), 4)
        for l in linhas:
            self.assertEqual(uuid.UUID(l).version, 4)

    def test_maiusculas_e_erro(self):
        self.assertTrue(rodar(["--seed", "1", "--maiusculas"])[1][0].isupper())
        with contextlib.redirect_stderr(io.StringIO()):
            self.assertEqual(main(["--seed", "1", "-n", "0"]), 1)


if __name__ == "__main__":
    unittest.main()
