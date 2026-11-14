import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from jur_procuracao import (MODELO_AD_JUDICIA, campos_do_modelo, campos_faltantes, preencher,
                            preencher_com_poderes_especiais)

VAL = {"outorgante": "Maria Silva", "documento": "CPF 529.982.247-25", "endereco": "Rua A, 1",
       "advogado": "Ana Souza", "uf": "SP", "oab": "123456", "poderes": "os da cláusula ad judicia",
       "cidade": "São Paulo", "data": "10/05/2024"}


class TestProcuracao(unittest.TestCase):
    def test_campos(self):
        self.assertEqual(campos_do_modelo("{{a}} {{ b }} {{a}}"), ["a", "b"])
        self.assertEqual(campos_do_modelo("sem campos"), [])

    def test_preencher(self):
        t = preencher(MODELO_AD_JUDICIA, VAL)
        self.assertIn("OUTORGANTE: Maria Silva", t)
        self.assertIn("OAB/SP 123456", t)
        self.assertNotIn("{{", t)

    def test_estrito(self):
        v = dict(VAL)
        del v["oab"]
        v["uf"] = "  "
        self.assertEqual(campos_faltantes(MODELO_AD_JUDICIA, v), ["uf", "oab"])
        with self.assertRaisesRegex(ValueError, "uf, oab"):
            preencher(MODELO_AD_JUDICIA, v)

    def test_nao_estrito_mantem_marcador(self):
        self.assertEqual(preencher("Olá {{nome}} {{x}}", {"nome": "Ana"}, estrito=False), "Olá Ana {{x}}")

    def test_valor_nao_reinterpretado(self):
        self.assertEqual(preencher("{{a}}", {"a": "{{b}}", "b": "x"}), "{{b}}")

    def test_poderes_especiais(self):
        t = preencher_com_poderes_especiais(MODELO_AD_JUDICIA, VAL, ["receber e dar quitação", "transigir"])
        self.assertIn("os da cláusula ad judicia, receber e dar quitação, transigir", t)
        v = {k: x for k, x in VAL.items() if k != "poderes"}
        self.assertIn("poderes gerais", preencher_com_poderes_especiais(MODELO_AD_JUDICIA, v, []))


if __name__ == "__main__":
    unittest.main()
