import sys
import tempfile
import unittest
from dataclasses import dataclass
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

import gen_arquivos as g
from gen_clientes import gerar_clientes


@dataclass
class Linha:
    a: int
    b: str


class TestGenArquivos(unittest.TestCase):
    def test_csv_roundtrip_com_virgulas_aspas_e_acentos(self):
        dados = [{"nome": 'João "Zé", Silva', "n": 1}, {"nome": "Maria\nSouza", "n": 2}]
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "x.csv"
            self.assertEqual(g.escrever_csv(dados, p), 2)
            lido = g.ler_csv(p)
        self.assertEqual(lido[0]["nome"], 'João "Zé", Silva')
        self.assertEqual(lido[1]["nome"], "Maria\nSouza")
        self.assertEqual([r["n"] for r in lido], ["1", "2"])

    def test_jsonl_roundtrip_e_uma_linha_por_registro(self):
        dados = [Linha(1, "é"), Linha(2, "linha\ncom quebra")]
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "x.jsonl"
            self.assertEqual(g.escrever_jsonl(dados, p), 2)
            texto = p.read_text(encoding="utf-8")
            lido = g.ler_jsonl(p)
        self.assertEqual(len(texto.splitlines()), 2)
        self.assertIn("é", texto)  # ensure_ascii desligado
        self.assertEqual(lido, [{"a": 1, "b": "é"}, {"a": 2, "b": "linha\ncom quebra"}])

    def test_colunas_heterogeneas(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "h.csv"
            g.escrever_csv([{"a": 1}, {"a": 2, "b": 3}], p)
            lido = g.ler_csv(p)
        self.assertEqual(lido, [{"a": "1", "b": ""}, {"a": "2", "b": "3"}])

    def test_clientes_achatados_e_datas(self):
        clientes = gerar_clientes(1, 25, date(2025, 1, 1))
        tmp, pc, pj = g.gerar_em_tempdir(clientes, "clientes")
        try:
            csv_ = g.ler_csv(pc)
            jl = g.ler_jsonl(pj)
            self.assertEqual(len(csv_), 25)
            self.assertEqual(len(jl), 25)
            self.assertIn("endereco.cep", csv_[0])
            self.assertEqual(csv_[3]["cpf"], clientes[3].cpf)
            self.assertEqual(jl[3]["endereco"]["cep"], clientes[3].endereco.cep)
            self.assertEqual(jl[3]["nascimento"], clientes[3].nascimento.isoformat())
            self.assertEqual(csv_[3]["nascimento"], clientes[3].nascimento.isoformat())
        finally:
            tmp.cleanup()
        self.assertFalse(pc.exists())

    def test_deterministico_byte_a_byte(self):
        c = gerar_clientes(5, 10, date(2025, 1, 1))
        t1, p1, _ = g.gerar_em_tempdir(c)
        t2, p2, _ = g.gerar_em_tempdir(c)
        try:
            self.assertEqual(p1.read_bytes(), p2.read_bytes())
        finally:
            t1.cleanup()
            t2.cleanup()

    def test_tipo_invalido(self):
        with tempfile.TemporaryDirectory() as d:
            with self.assertRaises(TypeError):
                g.escrever_jsonl([42], Path(d) / "x.jsonl")


if __name__ == "__main__":
    unittest.main()
