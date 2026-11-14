import os
import sys
import tempfile
import unittest
from io import StringIO
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from uni_paste import colar, colar_serial, main


class TestUniPaste(unittest.TestCase):
    def test_colar(self):
        self.assertEqual(colar([["a", "b"], ["1", "2"]]), ["a\t1", "b\t2"])

    def test_colunas_desiguais(self):
        self.assertEqual(colar([["a", "b"], ["1"]], ","), ["a,1", "b,"])

    def test_vazio(self):
        self.assertEqual(colar([]), [])

    def test_serial(self):
        self.assertEqual(colar_serial([["a", "b", "c"]], ","), ["a,b,c"])

    def test_main_arquivos(self):
        with tempfile.TemporaryDirectory() as d:
            p1, p2 = os.path.join(d, "1"), os.path.join(d, "2")
            Path(p1).write_text("a\nb\n", encoding="utf-8")
            Path(p2).write_text("x\ny\n", encoding="utf-8")
            s = StringIO()
            self.assertEqual(main(["-d", "-", p1, p2], "", s), 0)
            self.assertEqual(s.getvalue(), "a-x\nb-y\n")

    def test_main_stdin_serial(self):
        s = StringIO()
        main(["-s", "-d", ","], "1\n2\n3\n", s)
        self.assertEqual(s.getvalue(), "1,2,3\n")

    def test_main_arquivo_inexistente(self):
        self.assertEqual(main(["/nao/existe/xyz"], "", StringIO()), 1)

    def test_main_opcao_invalida(self):
        self.assertEqual(main(["-q"], "", StringIO()), 2)


if __name__ == "__main__":
    unittest.main()
