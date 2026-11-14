import os
import sys
import tempfile
import unittest
from io import StringIO
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from uni_wc import contar, formatar, main


class TestUniWc(unittest.TestCase):
    def test_contar(self):
        self.assertEqual(contar("a b\nc\n"), (2, 3, 6))

    def test_vazio(self):
        self.assertEqual(contar(""), (0, 0, 0))

    def test_sem_newline_final(self):
        self.assertEqual(contar("um dois"), (0, 2, 7))

    def test_bytes_utf8(self):
        self.assertEqual(contar("é")[2], 2)

    def test_formatar_opcoes(self):
        self.assertEqual(formatar((1, 2, 3), "w"), "2")
        self.assertEqual(formatar((1, 2, 3), ""), "1 2 3")

    def test_main_stdin(self):
        s = StringIO()
        self.assertEqual(main(["-l"], "a\nb\n", s), 0)
        self.assertEqual(s.getvalue(), "2\n")

    def test_main_opcao_invalida(self):
        self.assertEqual(main(["-x"], "", StringIO()), 2)

    def test_main_arquivo(self):
        with tempfile.TemporaryDirectory() as d:
            p = os.path.join(d, "a.txt")
            with open(p, "w", encoding="utf-8") as f:
                f.write("x y\n")
            s = StringIO()
            self.assertEqual(main(["-w", p], "", s), 0)
            self.assertEqual(s.getvalue(), f"2 {p}\n")

    def test_main_arquivo_inexistente(self):
        self.assertEqual(main(["/nao/existe/xyz"], "", StringIO()), 1)


if __name__ == "__main__":
    unittest.main()
