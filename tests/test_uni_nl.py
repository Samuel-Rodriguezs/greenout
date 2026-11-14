import sys
import unittest
from io import StringIO
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from uni_nl import main, numerar


class TestUniNl(unittest.TestCase):
    def test_numerar(self):
        self.assertEqual(numerar(["a", "b"]), ["     1\ta", "     2\tb"])

    def test_inicio(self):
        self.assertEqual(numerar(["a"], inicio=10), ["    10\ta"])

    def test_vazias_numeradas_por_padrao(self):
        self.assertEqual(numerar(["a", ""])[1], "     2\t")

    def test_ignorar_vazias(self):
        self.assertEqual(numerar(["a", "", "b"], ignorar_vazias=True),
                         ["     1\ta", "", "     2\tb"])

    def test_vazio(self):
        self.assertEqual(numerar([]), [])

    def test_main(self):
        s = StringIO()
        self.assertEqual(main(["-v", "5"], "x\n", s), 0)
        self.assertEqual(s.getvalue(), "     5\tx\n")

    def test_main_b(self):
        s = StringIO()
        main(["-b"], "a\n\nb\n", s)
        self.assertEqual(s.getvalue(), "     1\ta\n\n     2\tb\n")

    def test_main_erros(self):
        self.assertEqual(main(["-v", "x"], "", StringIO()), 2)
        self.assertEqual(main(["-v"], "", StringIO()), 2)
        self.assertEqual(main(["--foo"], "", StringIO()), 2)


if __name__ == "__main__":
    unittest.main()
