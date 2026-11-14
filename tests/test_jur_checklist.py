import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from jur_checklist import novo_checklist, pendencias_gerais


class TestChecklist(unittest.TestCase):
    def test_faltantes(self):
        c = novo_checklist("Trabalhista")
        self.assertEqual(c.faltantes(), ["cpf", "ctps", "procuração", "rg", "termo de rescisão"])
        self.assertIn("holerites", c.faltantes(incluir_opcionais=True))

    def test_receber(self):
        c = novo_checklist("trabalhista")
        for d in ("RG", " CPF ", "ctps"):
            c.receber(d)
        self.assertEqual(c.faltantes(), ["procuração", "termo de rescisão"])
        self.assertEqual(c.percentual(), 60.0)

    def test_completo(self):
        c = novo_checklist("consumidor")
        for d in ("rg", "cpf", "comprovante de residência", "contrato", "procuração"):
            c.receber(d)
        self.assertTrue(c.completo())
        self.assertEqual(c.percentual(), 100.0)
        c.estornar("contrato")
        self.assertFalse(c.completo())

    def test_documento_nao_previsto(self):
        with self.assertRaises(ValueError):
            novo_checklist("divorcio").receber("ctps")

    def test_tipo_desconhecido(self):
        with self.assertRaises(KeyError):
            novo_checklist("penal")

    def test_tabela_propria_e_sem_obrigatorios(self):
        c = novo_checklist("x", {"x": {"a": False}})
        self.assertEqual(c.percentual(), 100.0)
        self.assertTrue(c.completo())

    def test_pendencias_gerais(self):
        a, b = novo_checklist("consumidor"), novo_checklist("divorcio")
        for d in ("rg", "cpf", "comprovante de residência", "contrato", "procuração"):
            a.receber(d)
        r = pendencias_gerais({"P1": a, "P2": b})
        self.assertEqual(list(r), ["P2"])


if __name__ == "__main__":
    unittest.main()
