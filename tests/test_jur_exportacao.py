import sys
import unittest
from decimal import Decimal as D
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from dt_processo_cnj import montar_processo
from jur_exportacao import de_csv, para_csv, para_markdown
from jur_processos import criar_processo


def proc(seq: int, adv: str, valor: str):
    return criar_processo(montar_processo(seq, 2024, 8, 26, 1), "civel", adv, valor)


P = [proc(2, "Bia", "1234.5"), proc(1, "Ana; Souza", "10")]


class TestExportacao(unittest.TestCase):
    def test_csv_ordenado_e_roundtrip(self):
        txt = para_csv(P)
        linhas = txt.splitlines()
        self.assertEqual(linhas[0], "numero;area;advogado;fase;valor_causa")
        self.assertTrue(linhas[1].startswith("0000001"))
        volta = de_csv(txt)
        self.assertEqual(volta[0]["advogado"], "Ana; Souza")  # separador no conteúdo é citado
        self.assertEqual(volta[1]["valor_causa"], "1234.50")

    def test_csv_vazio(self):
        self.assertEqual(para_csv([]), "numero;area;advogado;fase;valor_causa\n")
        self.assertEqual(de_csv(para_csv([])), [])

    def test_csv_injecao_formula(self):
        p = criar_processo(montar_processo(3, 2024, 8, 26, 1), "civel", "=CMD()", 1)
        self.assertIn("'=CMD()", para_csv([p]))

    def test_csv_cabecalho_invalido(self):
        with self.assertRaises(ValueError):
            de_csv("a;b\n1;2\n")

    def test_markdown(self):
        md = para_markdown(P)
        linhas = md.splitlines()
        self.assertEqual(linhas[1], "|---|---|---|---|---:|")
        self.assertIn("R$ 1.234,50", md)
        self.assertEqual(linhas[-1], "| **Total (2)** | | | | **R$ 1.244,50** |")

    def test_markdown_escapa_pipe(self):
        p = criar_processo(montar_processo(4, 2024, 8, 26, 1), "civel", "A|B", D("1"))
        self.assertIn("A\\|B", para_markdown([p]))

    def test_markdown_vazio(self):
        self.assertIn("**Total (0)**", para_markdown([]))
        self.assertIn("R$ 0,00", para_markdown([]))


if __name__ == "__main__":
    unittest.main()
