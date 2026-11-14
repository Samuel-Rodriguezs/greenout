import os
import sys
import tempfile
import unittest
from io import StringIO
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from uni_comm import comparar, main


class TestUniComm(unittest.TestCase):
    def test_comparar(self):
        self.assertEqual(comparar(["a", "b", "d"], ["b", "c", "d"]),
                         [(1, "a"), (3, "b"), (2, "c"), (3, "d")])

    def test_vazios(self):
        self.assertEqual(comparar([], []), [])
        self.assertEqual(comparar(["a"], []), [(1, "a")])
        self.assertEqual(comparar([], ["a"]), [(2, "a")])

    def test_resto(self):
        self.assertEqual(comparar(["a"], ["a", "b", "c"]), [(3, "a"), (2, "b"), (2, "c")])

    def _arquivos(self, d, a, b):
        p1, p2 = os.path.join(d, "a"), os.path.join(d, "b")
        Path(p1).write_text(a, encoding="utf-8")
        Path(p2).write_text(b, encoding="utf-8")
        return p1, p2

    def test_main(self):
        with tempfile.TemporaryDirectory() as d:
            p1, p2 = self._arquivos(d, "a\nb\n", "b\nc\n")
            s = StringIO()
            self.assertEqual(main([p1, p2], "", s), 0)
            self.assertEqual(s.getvalue(), "a\n\t\tb\n\tc\n")

    def test_main_suprime(self):
        with tempfile.TemporaryDirectory() as d:
            p1, p2 = self._arquivos(d, "a\nb\n", "b\nc\n")
            s = StringIO()
            main(["-12", p1, p2], "", s)
            self.assertEqual(s.getvalue(), "b\n")
            s = StringIO()
            main(["-3", p1, p2], "", s)
            self.assertEqual(s.getvalue(), "a\n\tc\n")

    def test_main_erros(self):
        self.assertEqual(main(["x"], "", StringIO()), 2)
        self.assertEqual(main(["-9", "a", "b"], "", StringIO()), 2)
        self.assertEqual(main(["/nao/existe/1", "/nao/existe/2"], "", StringIO()), 1)


if __name__ == "__main__":
    unittest.main()
