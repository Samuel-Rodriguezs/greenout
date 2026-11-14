import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from csv_resumo import media_por_coluna


class TestCsv(unittest.TestCase):
    def test_medias(self):
        dados = "nome,nota,idade\nAna,8,20\nBia,6,22\n"
        self.assertEqual(media_por_coluna(dados), {"nota": 7.0, "idade": 21.0})


if __name__ == "__main__":
    unittest.main()
