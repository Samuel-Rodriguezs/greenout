import contextlib
import io
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from cli_renomear import main


class TestCliRenomear(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.TemporaryDirectory()
        self.pasta = Path(self.dir.name)
        for n in ("foto_1.jpg", "foto_2.jpg", "nota.txt"):
            (self.pasta / n).write_text(n)

    def tearDown(self):
        self.dir.cleanup()

    def rodar(self, *args):
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            code = main(list(args))
        return code, buf.getvalue()

    def nomes(self):
        return sorted(p.name for p in self.pasta.iterdir())

    def test_dry_run_nao_altera(self):
        code, out = self.rodar(str(self.pasta), "foto", "img", "--dry-run")
        self.assertEqual(code, 0)
        self.assertIn("foto_1.jpg -> img_1.jpg", out)
        self.assertIn("2 arquivo(s) a renomear", out)
        self.assertEqual(self.nomes(), ["foto_1.jpg", "foto_2.jpg", "nota.txt"])

    def test_renomeia(self):
        self.assertEqual(self.rodar(str(self.pasta), "foto", "img")[0], 0)
        self.assertEqual(self.nomes(), ["img_1.jpg", "img_2.jpg", "nota.txt"])

    def test_regex(self):
        self.rodar(str(self.pasta), r"_(\d)", r"-0\1", "--regex")
        self.assertEqual(self.nomes(), ["foto-01.jpg", "foto-02.jpg", "nota.txt"])

    def test_conflito(self):
        with contextlib.redirect_stderr(io.StringIO()):
            code, _ = self.rodar(str(self.pasta), r"_\d", "", "--regex")
        self.assertEqual(code, 1)
        self.assertEqual(self.nomes(), ["foto_1.jpg", "foto_2.jpg", "nota.txt"])

    def test_pasta_invalida(self):
        with contextlib.redirect_stderr(io.StringIO()):
            self.assertEqual(self.rodar("/nao/existe", "a", "b")[0], 1)


if __name__ == "__main__":
    unittest.main()
