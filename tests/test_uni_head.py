import sys
import unittest
from io import StringIO
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from uni_head import head, main


class TestUniHead(unittest.TestCase):
    def test_padrao_dez(self):
        self.assertEqual(len(head([str(i) for i in range(20)])), 10)

    def test_n_maior_que_total(self):
        self.assertEqual(head(["a", "b"], 5), ["a", "b"])

    def test_zero(self):
        self.assertEqual(head(["a"], 0), [])

    def test_negativo(self):
        with self.assertRaises(ValueError):
            head(["a"], -1)

    def test_main(self):
        s = StringIO()
        self.assertEqual(main(["-n", "2"], "a\nb\nc\n", s), 0)
        self.assertEqual(s.getvalue(), "a\nb\n")

    def test_main_sem_valor(self):
        self.assertEqual(main(["-n"], "", StringIO()), 2)

    def test_main_valor_nao_numerico(self):
        self.assertEqual(main(["-n", "x"], "", StringIO()), 2)

    def test_main_negativo(self):
        self.assertEqual(main(["-n", "-3"], "a\n", StringIO()), 2)

    def test_main_argumento_estranho(self):
        self.assertEqual(main(["foo"], "", StringIO()), 2)


if __name__ == "__main__":
    unittest.main()
