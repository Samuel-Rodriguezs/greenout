import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from dp_template_method import Importador, ImportadorCsv, ImportadorJson


class TestTemplateMethod(unittest.TestCase):
    def test_csv(self):
        bruto = "nome,email\nAna,ANA@X.COM\nBia,\n"
        self.assertEqual(ImportadorCsv().importar(bruto),
                         [{"nome": "Ana", "email": "ana@x.com"}])

    def test_json_valida_arroba(self):
        bruto = '[{"email": "a@b.c"}, {"email": "invalido"}, {"nome": "x"}]'
        self.assertEqual(ImportadorJson().importar(bruto), [{"email": "a@b.c"}])

    def test_csv_vazio(self):
        self.assertEqual(ImportadorCsv().importar(""), [])

    def test_abstrato(self):
        with self.assertRaises(TypeError):
            Importador()


if __name__ == "__main__":
    unittest.main()
