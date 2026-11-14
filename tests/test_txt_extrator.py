import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from txt_extrator import apenas_digitos, extrair_ceps, extrair_emails, extrair_telefones, extrair_tudo


class TestExtrator(unittest.TestCase):
    def test_emails(self):
        self.assertEqual(
            extrair_emails("Fale com ana.silva@exemplo.com.br ou bob+x@site.org."),
            ["ana.silva@exemplo.com.br", "bob+x@site.org"],
        )
        self.assertEqual(extrair_emails("sem email @aqui"), [])

    def test_telefones(self):
        t = "Ligue (11) 98765-4321 ou 21 3456-7890 ou 3456-7890 ou 11987654321."
        self.assertEqual(
            extrair_telefones(t),
            ["(11) 98765-4321", "21 3456-7890", "3456-7890", "11987654321"],
        )

    def test_ceps(self):
        self.assertEqual(extrair_ceps("CEP 01310-100 e 22040020"), ["01310-100", "22040020"])
        self.assertEqual(extrair_ceps("123456789"), [])

    def test_cep_nao_vira_telefone(self):
        self.assertEqual(extrair_telefones("CEP 01310-100"), [])

    def test_tudo_e_vazio(self):
        self.assertEqual(extrair_tudo(""), {"emails": [], "telefones": [], "ceps": []})
        self.assertEqual(extrair_tudo("a@b.co 01310-100")["ceps"], ["01310-100"])

    def test_digitos(self):
        self.assertEqual(apenas_digitos("(11) 98765-4321"), "11987654321")


if __name__ == "__main__":
    unittest.main()
