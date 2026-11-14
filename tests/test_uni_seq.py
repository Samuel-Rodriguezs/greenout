import sys
import unittest
from io import StringIO
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from uni_seq import main, sequencia


class TestUniSeq(unittest.TestCase):
    def test_crescente(self):
        self.assertEqual(sequencia(1, 1, 5), [1, 2, 3, 4, 5])

    def test_passo(self):
        self.assertEqual(sequencia(1, 3, 10), [1, 4, 7, 10])

    def test_decrescente(self):
        self.assertEqual(sequencia(5, -2, 0), [5, 3, 1])

    def test_vazia(self):
        self.assertEqual(sequencia(5, 1, 1), [])
        self.assertEqual(sequencia(1, -1, 5), [])

    def test_unico(self):
        self.assertEqual(sequencia(3, 1, 3), [3])

    def test_passo_zero(self):
        with self.assertRaises(ValueError):
            sequencia(1, 0, 5)

    def test_main_formas(self):
        for argv, esperado in ((["3"], "1\n2\n3\n"), (["2", "4"], "2\n3\n4\n"),
                               (["10", "-5", "0"], "10\n5\n0\n")):
            s = StringIO()
            self.assertEqual(main(argv, "", s), 0)
            self.assertEqual(s.getvalue(), esperado)

    def test_main_erros(self):
        self.assertEqual(main([], "", StringIO()), 2)
        self.assertEqual(main(["a"], "", StringIO()), 2)
        self.assertEqual(main(["1", "0", "5"], "", StringIO()), 2)
        self.assertEqual(main(["1", "2", "3", "4"], "", StringIO()), 2)


if __name__ == "__main__":
    unittest.main()
