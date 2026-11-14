import os
import sys
import tempfile
import unittest
from io import StringIO
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from uni_tac import main, tac


class TestUniTac(unittest.TestCase):
    def test_tac(self):
        self.assertEqual(tac(["1", "2", "3"]), ["3", "2", "1"])

    def test_vazio(self):
        self.assertEqual(tac([]), [])

    def test_nao_altera_original(self):
        orig = ["a", "b"]
        tac(orig)
        self.assertEqual(orig, ["a", "b"])

    def test_main_stdin(self):
        s = StringIO()
        self.assertEqual(main([], "a\nb\n", s), 0)
        self.assertEqual(s.getvalue(), "b\na\n")

    def test_main_arquivo(self):
        with tempfile.TemporaryDirectory() as d:
            p = os.path.join(d, "f")
            Path(p).write_text("x\ny\n", encoding="utf-8")
            s = StringIO()
            self.assertEqual(main([p], "", s), 0)
            self.assertEqual(s.getvalue(), "y\nx\n")

    def test_main_inexistente(self):
        self.assertEqual(main(["/nao/existe/xyz"], "", StringIO()), 1)


if __name__ == "__main__":
    unittest.main()
