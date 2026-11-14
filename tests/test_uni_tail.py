import sys
import unittest
from io import StringIO
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from uni_tail import main, tail


class TestUniTail(unittest.TestCase):
    def test_ultimas(self):
        self.assertEqual(tail(["a", "b", "c"], 2), ["b", "c"])

    def test_n_maior_que_total(self):
        self.assertEqual(tail(["a", "b"], 5), ["a", "b"])

    def test_zero(self):
        self.assertEqual(tail(["a", "b"], 0), [])

    def test_vazio(self):
        self.assertEqual(tail([], 3), [])

    def test_negativo(self):
        with self.assertRaises(ValueError):
            tail(["a"], -2)

    def test_main(self):
        s = StringIO()
        self.assertEqual(main(["-n", "1"], "a\nb\nc\n", s), 0)
        self.assertEqual(s.getvalue(), "c\n")

    def test_main_padrao(self):
        s = StringIO()
        main([], "\n".join(str(i) for i in range(15)), s)
        self.assertEqual(len(s.getvalue().splitlines()), 10)

    def test_main_erros(self):
        self.assertEqual(main(["-n"], "", StringIO()), 2)
        self.assertEqual(main(["-n", "abc"], "", StringIO()), 2)
        self.assertEqual(main(["-n", "-1"], "a\n", StringIO()), 2)


if __name__ == "__main__":
    unittest.main()
