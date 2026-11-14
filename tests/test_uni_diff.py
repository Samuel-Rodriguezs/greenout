import os
import sys
import tempfile
import unittest
from io import StringIO
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from uni_diff import diff, main


class TestUniDiff(unittest.TestCase):
    def test_iguais(self):
        self.assertEqual(diff(["a", "b"], ["a", "b"]), [(" ", "a"), (" ", "b")])

    def test_vazios(self):
        self.assertEqual(diff([], []), [])

    def test_so_adicoes(self):
        self.assertEqual(diff([], ["x"]), [("+", "x")])

    def test_so_remocoes(self):
        self.assertEqual(diff(["x"], []), [("-", "x")])

    def test_troca_no_meio(self):
        ops = diff(["a", "b", "c"], ["a", "X", "c"])
        self.assertEqual([o for o, _ in ops if o != " "].count("-"), 1)
        self.assertIn(("-", "b"), ops)
        self.assertIn(("+", "X"), ops)
        self.assertEqual(ops[0], (" ", "a"))
        self.assertEqual(ops[-1], (" ", "c"))

    def test_reconstrucao(self):
        a = list("ABCABBA")
        b = list("CBABAC")
        ops = diff(a, b)
        self.assertEqual([l for o, l in ops if o != "+"], a)
        self.assertEqual([l for o, l in ops if o != "-"], b)
        # LCS de ABCABBA e CBABAC tem tamanho 4
        self.assertEqual(sum(1 for o, _ in ops if o == " "), 4)

    def _par(self, d, a, b):
        p1, p2 = os.path.join(d, "a"), os.path.join(d, "b")
        Path(p1).write_text(a, encoding="utf-8")
        Path(p2).write_text(b, encoding="utf-8")
        return p1, p2

    def test_main_diferentes(self):
        with tempfile.TemporaryDirectory() as d:
            p1, p2 = self._par(d, "a\nb\n", "a\nc\n")
            s = StringIO()
            self.assertEqual(main([p1, p2], "", s), 1)
            self.assertEqual(s.getvalue(), "- b\n+ c\n")

    def test_main_iguais(self):
        with tempfile.TemporaryDirectory() as d:
            p1, p2 = self._par(d, "a\n", "a\n")
            s = StringIO()
            self.assertEqual(main([p1, p2], "", s), 0)
            self.assertEqual(s.getvalue(), "")

    def test_main_erros(self):
        self.assertEqual(main(["a"], "", StringIO()), 2)
        self.assertEqual(main(["/nao/existe/1", "/nao/existe/2"], "", StringIO()), 2)


if __name__ == "__main__":
    unittest.main()
