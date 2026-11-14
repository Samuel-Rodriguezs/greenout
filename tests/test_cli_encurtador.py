import contextlib
import io
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from cli_encurtador import codigo, main


class TestCliEncurtador(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.TemporaryDirectory()
        self.arq = str(Path(self.dir.name) / "l.json")

    def tearDown(self):
        self.dir.cleanup()

    def rodar(self, *args):
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            code = main(["--arquivo", self.arq, *args])
        return code, buf.getvalue().strip()

    def test_encurtar_e_resolver(self):
        _, c = self.rodar("encurtar", "https://exemplo.com/a")
        self.assertEqual(self.rodar("resolver", c), (0, "https://exemplo.com/a"))

    def test_idempotente(self):
        a = self.rodar("encurtar", "https://x.com")[1]
        b = self.rodar("encurtar", "https://x.com")[1]
        self.assertEqual(a, b)

    def test_codigos_distintos_e_listar(self):
        a = self.rodar("encurtar", "https://a.com")[1]
        b = self.rodar("encurtar", "https://b.com")[1]
        self.assertNotEqual(a, b)
        self.assertEqual(len(self.rodar("listar")[1].splitlines()), 2)

    def test_erros(self):
        with contextlib.redirect_stderr(io.StringIO()):
            self.assertEqual(self.rodar("encurtar", "ftp://x")[0], 1)
            self.assertEqual(self.rodar("resolver", "zzz")[0], 1)

    def test_codigo(self):
        self.assertEqual(codigo(0), "0")
        self.assertEqual(codigo(62), "10")


if __name__ == "__main__":
    unittest.main()
